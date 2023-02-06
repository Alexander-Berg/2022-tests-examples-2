[default]

[tcpout]
disabled = false
#compressed = true
forwardedindex.filter.disable = true
indexAndForward = false
defaultGroup = splunk_forwarder

[tcpout:splunk_forwarder]
server = {{ SPLUNK_HOST }}:3333
#clientCert = $SPLUNK_HOME/etc/auth/server.pem
#sslPassword = password
#token = 4CF05A0C-5CA8-478F-9F08-D2F8AFBF74DB
#useSSL = true
