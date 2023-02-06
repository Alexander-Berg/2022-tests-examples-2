package ru.yandex.metrika.dbclients.config;

import java.util.Map;

public class MdsTestConfig {

    private final String endpoint;
    private final String accessKey;
    private final String secretKey;

    public MdsTestConfig(String endpoint, String accessKey, String secretKey) {
        this.endpoint = endpoint;
        this.accessKey = accessKey;
        this.secretKey = secretKey;
    }

    public String getEndpoint() {
        return endpoint;
    }

    public String getAccessKey() {
        return accessKey;
    }

    public String getSecretKey() {
        return secretKey;
    }

    public Map<String, String> asFtlParams() {
        return Map.of(
                "mdsEndpoint", endpoint,
                "mdsAccessKey", accessKey,
                "mdsSecretKey", secretKey
        );
    }
}
