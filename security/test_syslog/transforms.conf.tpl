# For events routed to /dev/null
# [setnull]
# REGEX = .
# DEST_KEY = queue
# FORMAT = nullQueue

# Forward rest events to index MAIN
[main]
REGEX = .
DEST_KEY = queue
FORMAT = indexQueue


[set_sourcetype_openvpn]
REGEX = ^\S+\sopenvpn-.*
FORMAT = sourcetype::syslog_openvpn
DEST_KEY = MetaData:Sourcetype


[set_sourcetype_oracle]
REGEX = ^\S+\sabs-ora-db-.*
FORMAT = sourcetype::syslog_oracle
DEST_KEY = MetaData:Sourcetype


[set_sourcetype_vault]
REGEX = ^\S+\svault-.*
FORMAT = sourcetype::syslog_vault
DEST_KEY = MetaData:Sourcetype


[set_sourcetype_teleport_1]
REGEX = ^\S+\steleport-auth-.*
FORMAT = sourcetype::syslog_teleport
DEST_KEY = MetaData:Sourcetype

[set_sourcetype_teleport_2]
REGEX = ^\S+\stp-auth-.*
FORMAT = sourcetype::syslog_teleport
DEST_KEY = MetaData:Sourcetype

[set_sourcetype_squid_1]
REGEX = ^\S+\ssquid-.*
FORMAT = sourcetype::syslog_squid
DEST_KEY = MetaData:Sourcetype

[set_sourcetype_squid_2]
REGEX = ^\S+\s[0-9a-z]{2,5}\-proxy\-.*
FORMAT = sourcetype::ssyslog_squid
DEST_KEY = MetaData:Sourcetype

[squid_setnull]
REGEX = error:transaction-end-before-headers
DEST_KEY = queue
FORMAT = nullQueue
