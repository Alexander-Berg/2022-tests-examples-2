FROM splunk/splunk:latest

#ENV SPLUNK_START_ARGS=--accept-license
#ENV SPLUNK_PASSWORD=<password>
#ENV OPENSSL_CONF=$SPLUNK_HOME/openssl/openssl.cnf
WORKDIR $SPLUNK_HOME
#RUN rm -rf $SPLUNK_HOME/etc/system/local/inputs.conf
#RUN rm -rf $SPLUNK_HOME/etc/system/local/outputs.conf
COPY *.conf $SPLUNK_HOME/etc/system/local/
#COPY outputs.conf $SPLUNK_HOME/etc/system/local/outputs.conf


#https://docs.splunk.com/Documentation/Splunk/latest/Data/HowSplunkEnterprisehandlessyslogdata