package ru.yandex.autotests.metrika.appmetrica.parameters;

/**
 * Created by graev on 30/01/2017.
 */
public enum CARetention {
    CLASSIC("classic"),
    ROLLING("rolling"),
    EMPTY("");

    private final String apiName;

    CARetention(String apiName) {
        this.apiName = apiName;
    }

    public String getApiName() {
        return apiName;
    }

    @Override
    public String toString() {
        return apiName;
    }
}
