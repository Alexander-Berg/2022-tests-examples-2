[default]
ignoreOlderThan = 30d

###### OS Logs ######
[WinEventLog://Application]
disabled = 1
start_from = oldest
current_only = 0
checkpointInterval = 5
renderXml=false
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}


[WinEventLog://Security]
disabled = 0
start_from = oldest
current_only = 0
evt_resolve_ad_obj = 0
checkpointInterval = 5
blacklist1 = EventCode="4662" Message="Object Type:\s+*?!groupPolicyContainer"
blacklist2 = EventCode="566" Message="Object Type:\s+*?!groupPolicyContainer"
renderXml=false
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}

[WinEventLog://System]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
renderXml=false
whitelist = EventCode="5722|5723|5805"
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}


# SOC-1129
[WinEventLog://ForwardedEvents]
disabled = 0
start_from = oldest
current_only = 0
evt_resolve_ad_obj = 0
checkpointInterval = 5
renderXml=false
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}


###### Microsoft-Windows-CAPI2/Operational - TMG Servers (WINADMINREQ-5305) ######
# WARNING: NOT CONTROLLED VIA DS - MUST BE UPDATED MANUALLY ON SERVERS
[WinEventLog://Microsoft-Windows-CAPI2/Operational]
disabled = 0
start_from = oldest
current_only = 1
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}
renderXml=true

[WinEventLog://Microsoft-Windows-TerminalServices-LocalSessionManager/Operational]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}
renderXml=false

[WinEventLog://Microsoft-Windows-TerminalServices-LocalSessionManager/Admin]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}
renderXml=false

[WinEventLog://Microsoft-Windows-TerminalServices-RemoteConnectionManager/Admin]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}
renderXml=false

[WinEventLog://Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}
renderXml=false

[WinEventLog://Microsoft-Windows-TerminalServices-RDPClient/Operational]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}
renderXml=false

# SOC-1917
[WinEventLog://Microsoft-Windows-NTLM/Operational]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}
renderXml=false

[XmlWinEventLog://Microsoft-Windows-TerminalServices-LocalSessionManager/Admin]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}

[XmlWinEventLog://Microsoft-Windows-TerminalServices-LocalSessionManager/Operational]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}

[XmlWinEventLog://Microsoft-Windows-TerminalServices-RemoteConnectionManager/Admin]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}

[XmlWinEventLog://Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}

[XmlWinEventLog://Microsoft-Windows-TerminalServices-RDPClient/Operational]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
sourcetype = {{ SOURCETUPE_WIN_LOGS }}
index = {{ INDEX_WIN_LOGS }}