@version: 3.31

# https://www.splunk.com/en_us/blog/tips-and-tricks/splunk-connect-for-syslog-turnkey-and-scalable-syslog-gdi.html

options {
    chain_hostnames(off);
    use_dns(yes);
    use_fqdn(yes);
};

source s_net {
    network(
        transport("tcp")
        port(514)
    );
    network(
        transport("udp")
        port(514)
    );
};

destination d_HEC {
    http(
        url(
            "https://{{ HEC_HOST }}:{{ HEC_PORT }}/services/collector/event"
            )
        method("POST")
        batch-lines(10)
        batch-bytes(512Kb)
        batch-timeout(5000)
        user_agent("syslog-ng User Agent")
        user("syslog-ng")
        password("{{ HEC_TOKEN }}")
        persist-name("{{ HEC_HOST }}_{{ SPLUNK_SYSLOG_SOURCETYPE }}_{{ HEC_TOKEN }}_{{ SPLUNK_SYSLOG_INDEX }}")
        tls(peer-verify(no))
        body(
            '$(format-json 
                    time=$S_UNIXTIME.$S_MSEC
                    host=$HOST
                    source=${HOST_FROM}
                    sourcetype={{ SPLUNK_SYSLOG_SOURCETYPE }}
                    index={{ SPLUNK_SYSLOG_INDEX }}
                    event="${ISODATE} ${HOST} ${MESSAGE}"
              )'
            )
    );
};

log {
    source(s_net);
    destination(d_HEC);
};
