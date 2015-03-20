freeswitch.consoleLog("NOTICE", "Hello lua log!\n")

api = freeswitch.API()
reply = api:execute("version", "")
freeswitch.consoleLog("INFO", "Got reply:\n\n" .. reply .. "\n")
