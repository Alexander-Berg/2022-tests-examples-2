package ru.yandex.autotests.metrika.appmetrica.parameters;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * Created by graev on 14/02/2017.
 */
public enum CAMetric {
    DEVICES("devices"),
    EVENTS("events"),
    REVENUE("revenue"),
    PURCHASES("purchases"),
    PAYING_USERS("paying_users");

    /**
     * Метрики по стартам сессий и клиентским событиям.
     */
    public static final List<CAMetric> EVENT_METRICS = asList(DEVICES, EVENTS);
    /**
     * Метрики по событиям revenue.
     */
    public static final List<CAMetric> REVENUE_METRICS = asList(REVENUE, PURCHASES, PAYING_USERS);

    private final String apiName;

    CAMetric(String apiName) {
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
