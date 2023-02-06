#!/bin/bash

set -e

cd /opt/atp/src/

sed -i "s#{{APP_SECRET}}#$APP_SECRET#" config.yaml
sed -i "s#{{HEC_TOKEN}}#$HEC_TOKEN#" config.yaml

#sed -i "s#{{SPLUNK_INDEX_ALERTS}}#$SPLUNK_INDEX_ALERTS#" config.yaml
#sed -i "s#{{SPLUNK_SOURCETYPE_ALERTS}}#$SPLUNK_SOURCETYPE_ALERTS#" config.yaml

#sed -i "s#{{SPLUNK_INDEX_HOSTS}}#$SPLUNK_INDEX_HOSTS#" config.yaml
#sed -i "s#{{SPLUNK_SOURCETYPE_HOSTS}}#$SPLUNK_SOURCETYPE_HOSTS#" config.yaml

#sed -i "s#{{SPLUNK_INDEX_HOSTS}}#$SPLUNK_INDEX_HOSTS#" config.yaml
#sed -i "s#{{SPLUNK_SOURCETYPE_HOSTS}}#$SPLUNK_SOURCETYPE_HOSTS#" config.yaml

#ERR execution failed: locale::facet::_S_create_c_locale
export LC_ALL=C
unset LANGUAGE

# запускаем
/opt/venv/bin/python /opt/atp/src/main.py