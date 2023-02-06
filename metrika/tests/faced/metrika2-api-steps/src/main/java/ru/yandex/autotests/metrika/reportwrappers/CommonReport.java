package ru.yandex.autotests.metrika.reportwrappers;

import org.apache.commons.lang3.tuple.Pair;
import ru.yandex.metrika.api.constructor.response.QueryExternal;

import java.util.Collection;
import java.util.List;
import java.util.stream.IntStream;

/**
 * Created by omaz on 13.07.2015.
 */
public abstract class CommonReport<T> implements Report {

    protected final T rawReport;

    public CommonReport(T rawReport) {
        this.rawReport = rawReport;
    }

    protected static int getMetricIndex(List<String> metrics, String metricName) {
        return IntStream.range(0, metrics.size()).boxed()
                .map(i -> Pair.of(i, metrics.get(i)))
                .filter(p -> p.getValue().equals(metricName))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException(metricName))
                .getKey();
    }

    protected static int getDimensionIndex(List<String> dimensions, String dimensionName) {
        return IntStream.range(0, dimensions.size()).boxed()
                .map(i -> Pair.of(i, dimensions.get(i)))
                .filter(p -> p.getValue().equals(dimensionName))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException(dimensionName))
                .getKey();
    }
}
