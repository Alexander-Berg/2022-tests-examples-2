--- QoS Configs for resources
ALTER TABLE api_proxy.resources
    ADD COLUMN qos_taxi_config TEXT NULL DEFAULT NULL;
