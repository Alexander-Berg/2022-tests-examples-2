package ru.yandex.autotests.metrika.filters;

/**
 * Created by konkov on 13.05.2015.
 */
public class MetricExpression {

    public static String metricFunction(String func, String metric) {
        return String.format("%s(%s)", func, metric);
    }
    public static String metricFilter(String metric, Expression metricFilter) {
        return String.format("%s[%s]", metric, metricFilter.build());
    }
    public static String metricFilter2(String metric, Expression metricFilter) {
        return String.format("%s(%s)", metric, metricFilter.build());
    }
}
