SERVICE_CLUSTER=$1
ENVOY_RTC_CONFIG_PATH=/arcadia/taxi/backend-py3/services/envoy-rtc-config

if [ -d "${ENVOY_RTC_CONFIG_PATH}" ]; then
    cp -var "${ENVOY_RTC_CONFIG_PATH}"/etc/* /etc/
else
    echo "Do not update envoy configs"
fi

# XXX: wait util envoy is started
# run envoy in background so it doesn't block current script
/usr/bin/envoy -c /etc/envoy/envoy.yaml --service-cluster $SERVICE_CLUSTER --service-node $HOSTNAME --service-zone vla &
