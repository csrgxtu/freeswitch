freeswitch.consoleLog("NOTICE","lua take the users...\n");
-- gen_dir_user_xml.lua
-- example script for generating user directory XML

-- comment the following line for production:
-- freeswitch.consoleLog("notice", "Debug from gen_dir_user_xml.lua, provided params:\n" .. params:serialize() .. "\n")

local req_domain   = params:getHeader("domain")
local req_key      = params:getHeader("key")
local req_user     = params:getHeader("user")
local req_password = params:getHeader("pass")

local dbh = freeswitch.Dbh("freeswitch","freeswitch","fsadmin2009a")
assert(dbh:connected())

dbh:query("select sip_password from User where sip_number="..req_user .. " limit 1",function(row)
        if(row == nil or row.sip_password == nil) then
          freeswitch.consoleLog("NOTICE",string.format("user %s was not found in database!",req_user))
          return
        end
        freeswitch.consoleLog("NOTICE",string.format("%s\n",row.sip_password))
        req_password=row.sip_password
end);
dbh:release();

freeswitch.consoleLog("NOTICE","info:" .. req_domain .. "--" .. req_key .. "--" .. req_user .. "\n");



--assert (req_domain and req_key and req_user,
--"This example script only supports generating directory xml for a single user !\n")
if req_domain ~= nil and req_key~=nil and req_user~=nil then
    XML_STRING =
    [[<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <document type="freeswitch/xml">
      <section name="directory">
        <domain name="]]..req_domain..[[">
          <params>
            <param name="dial-string" value="{presence_id=${dialed_user}@${dialed_domain}}${sofia_contact(${dialed_user}@${dialed_domain})}"/>
          </params>
          <groups>
            <group name="default">
              <users>
                <user id="]] ..req_user..[[">
                  <params>
                    <param name="password" value="]]..req_password..[["/>
                    <param name="vm-password" value="]]..req_password..[["/>
                  </params>
                  <variables>
                    <variable name="toll_allow" value="domestic,international,local"/>
                    <variable name="accountcode" value="]] ..req_user..[["/>
                    <variable name="user_context" value="default"/>
                    <variable name="directory-visible" value="true"/>
                    <variable name="directory-exten-visible" value="true"/>
                    <variable name="limit_max" value="15"/>
                    <variable name="effective_caller_id_name" value="Extension ]] ..req_user..[["/>
                    <variable name="effective_caller_id_number" value="]] ..req_user..[["/>
                    <variable name="outbound_caller_id_name" value="${outbound_caller_name}"/>
                    <variable name="outbound_caller_id_number" value="${outbound_caller_id}"/>
                    <variable name="callgroup" value="techsupport"/>
                  </variables>
                </user>
              </users>
            </group>
          </groups>
        </domain>
      </section>
    </document>]]
else
    XML_STRING =
    [[<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <document type="freeswitch/xml">
      <section name="directory">
      </section>
    </document>]]
end

-- comment the following line for production:
--freeswitch.consoleLog("notice", "Debug from gen_dir_user_xml.lua, generated XML:\n" .. XML_STRING .. "\n");
