package ru.yandex.autotests.metrika.data.analytics.v3.enums;

/**
 * Created by sourx on 24.03.2016.
 */
public enum AnalyticsSampleAccuracyEnum {
    HIGHER_PRECISION("HIGHER_PRECISION"),
    FASTER("FASTER"),
    DEFAULT("DEFAULT");

    private final String accuracy;

    AnalyticsSampleAccuracyEnum(String accuracy) {
        this.accuracy = accuracy;
    }

    public String getAccuracy() {
        return accuracy;
    }
}