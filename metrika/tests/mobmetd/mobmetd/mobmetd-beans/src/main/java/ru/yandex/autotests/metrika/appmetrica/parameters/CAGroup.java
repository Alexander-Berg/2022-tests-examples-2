package ru.yandex.autotests.metrika.appmetrica.parameters;

/**
 * Created by graev on 30/01/2017.
 */
public enum CAGroup {
    DAY("day"),
    WEEK("week"),
    MONTH("month");

    private final String apiName;

    CAGroup(String apiName) {
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
