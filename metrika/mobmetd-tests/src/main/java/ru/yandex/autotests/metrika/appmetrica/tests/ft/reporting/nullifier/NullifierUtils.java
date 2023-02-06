package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.nullifier;

import org.hamcrest.Matcher;

import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;

public class NullifierUtils {

    public static Matcher<Double> NOT_NULL_ROW_MATCHER = notNullValue(Double.class);

    public static Matcher<Double> NULL_ROW_MATCHER = nullValue(Double.class);

    /**
     * немножко приведений типов, чтобы matcher-ы были нами довольны
     */
    public static List<Iterable<Double>> toIterable(List<List<Double>> row) {
        return row.stream()
                .map(d -> (Iterable<Double>) d)
                .collect(Collectors.toList());
    }
}
