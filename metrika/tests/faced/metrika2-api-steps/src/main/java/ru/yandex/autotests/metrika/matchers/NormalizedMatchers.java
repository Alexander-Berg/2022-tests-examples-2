package ru.yandex.autotests.metrika.matchers;

import java.util.List;

import org.hamcrest.Matcher;

import static org.hamcrest.CoreMatchers.nullValue;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.closeTo;

/**
 * матчеры для метрик, нормированных на 100%
 */
public class NormalizedMatchers {

    private NormalizedMatchers() {
    }

    public static Matcher<List<List<Double>>> areNormalized(List<List<Double>> rawMetrics, List<Double> rawTotals) {
        return new ListMatchers<>(rawMetrics.size(), i -> isNormalized(rawMetrics.get(i), rawTotals));
    }

    public static Matcher<List<Double>> isNormalized(List<Double> rawMetric, List<Double> rawTotals) {
        return new ListMatchers<>(rawMetric.size(),
                i -> rawMetric.get(i) != null && rawTotals.get(i) != null && rawTotals.get(i) != 0.0,
                i -> {
                    Double metric = rawMetric.get(i);
                    Double total = rawTotals.get(i);
                    double expected = metric / total * 100;
                    // для очень маленьких значений надо увеличивать размер ошибки, т.к. после округления и деления она может стать большой.
                    // дефолное форматирование флоатов оставляет разное количество значащих цифр в зависимости от порядка значения,
                    // поэтому кроме коэффициента value * epsilon есть еще один подгоночный множитель.
                    double error = Math.abs(expected) * 1E-6;
                    error = error * (metric != 0.0 && Math.abs(metric) < 1.0 ? 1 / Math.abs(metric) : 1);
                    error = Math.max(error, 10E-8);
                    return anyOf(nullValue(Double.class), closeTo(expected, error));
                });
    }

    public static Matcher<List<Double>> isNormalized(List<Double> rawMetric, Double total) {
        return new ListMatchers<>(rawMetric.size(),
                i -> rawMetric.get(i) != null && total != null && total != 0.0,
                i -> {
                    Double metric = rawMetric.get(i);
                    double expected = metric / total * 100;
                    double error = Math.abs(expected) * 1E-5;
                    error = Math.max(error, 10E-8);
                    return anyOf(nullValue(Double.class), closeTo(expected, error));
                });
    }

}
