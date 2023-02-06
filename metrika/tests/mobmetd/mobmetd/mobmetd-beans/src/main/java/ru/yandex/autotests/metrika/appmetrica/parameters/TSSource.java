package ru.yandex.autotests.metrika.appmetrica.parameters;

public enum TSSource {
    INSTALLATION("installation"),
    NEW_INSTALLATION("new_installation"),
    REATTRIBUTION("reattribution"),
    REENGAGEMENT("reengagement");

    private final String apiName;

    TSSource(String apiName) {
        this.apiName = apiName;
    }

    public String apiName() {
        return apiName;
    }
}
