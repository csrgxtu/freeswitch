function session_hangup_hook(status)
  freeswitch.consoleLog("NOTICE", string.format("session_hangup_hook ==> UPDATE ptt_groups SET current_speaker_id = 0, start_time='2000-01-01 00:00:00' WHERE ptt_number=%s and current_speaker_id=%s\n", ptt_number, caller_number))
  db:query(string.format("UPDATE ptt_groups SET current_speaker_id = 0, start_time='2000-01-01 00:00:00' WHERE ptt_number=%s and current_speaker_id=%s", ptt_number, caller_number), function(row)
    if (row == nil) then
      freeswitch.consoleLog("NOTICE", "PTT fuck")
    end
  )
  db:release()
end

session:answer();
session:setHangupHook("session_hangup_hook")

ptt_number = session:getVariable("destination_number")
caller_number = session:getVariable("caller_id_number")
db = freeswitch.Dbh("odbc://freeswitch:ebuserxft:ebtx@df74d78&")
assert(db:connected())
freeswitch.consoleLog("NOTICE","database connected")

if(session:ready()) then
  local members = {}
  freeswitch.consoleLog("NOTICE","database query " .. string.format("SELECT ptt_members,current_speaker_id,start_time FROM ptt_groups WHERE ptt_number=%s", ptt_number))
  db:query(string.format("SELECT ptt_members,current_speaker_id,start_time FROM ptt_groups WHERE ptt_number=%s", ptt_number), function(row)
    if(row == nil) then
      freeswitch.consoleLog("NOTICE", "PTT Number: " .. ptt_number .. " not found in database!")
      return
    end
    freeswitch.consoleLog("NOTICE", string.format("Current Speaker: %s, PTT Members: %s\n", row.current_speaker_id, row.ptt_members))
    if(row.current_speaker_id ~= "0") then
      freeswitch.consoleLog("NOTICE", "Current speaker is: " .. tostring(row.current_speaker_id) .. " add " .. tonumber(caller_number))
      freeswitch.consoleLog("NOTICE", "Start Conference: " .. session:getVariable("domain") .. "@default+flags{mute}")
      session:execute("conference",ptt_number .. session:getVariable("domain") .. "@default+flags{mute}")
    else
      for member in string.gmatch(row.ptt_members, '([^,]+)') do
        if(member ~= caller_number) then
          table.insert(members, string.format("user/%s",tostring(member)))
        end
      end

      freeswitch.consoleLog("NOTICE", string.format("UPDATE ptt_groups SET current_speaker_id = %s, start_time=now() WHERE ptt_number=%s", caller_number, ptt_number))
      db:query(string.format("UPDATE ptt_groups SET current_speaker_id = %s, start_time=now() WHERE ptt_number=%s", caller_number, ptt_number))
      session:execute("set","conference_auto_outcall_timeout=5")
      session:execute("set","conference_auto_outcall_flags=none")
      session:execute("set","conference_auto_outcall_caller_id_name=PTT" .. ptt_number)
      session:execute("set","conference_auto_outcall_caller_id_number=" .. caller_number)
      session:execute("set","conference_auto_outcall_profile=internal")
      session:execute("set","conference_auto_outcall_flags=mute")
      session.execute("set","conference_auto_outcall_endconf_grace_time=300")
      freeswitch.consoleLog("NOTICE", "conference_set_auto_outcall => " .. table.concat(members,","))
      session:execute("conference_set_auto_outcall",table.concat(members,","))
      freeswitch.consoleLog("NOTICE", "conference => " .. ptt_number .. session:getVariable("domain") .. "@default+flags{endconf|nomoh|moderator}")
      session:execute("conference",ptt_number .. session:getVariable("domain") .. "@default+flags{endconf|nomoh|moderator}")
    end
  end)

end

session:hangup()
