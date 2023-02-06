[source::tcp:4444]
SHOULD_LINEMERGE=False



[{{ SPLUNK_SYSLOG_SOURCETYPE }}]
TRANSFORMS-setsourcetype = set_sourcetype_openvpn, set_sourcetype_oracle, set_sourcetype_vault, set_sourcetype_teleport_1, set_sourcetype_teleport_2,set_sourcetype_squid_1,set_sourcetype_squid_2
TRANSFORMS-set = squid_setnull
