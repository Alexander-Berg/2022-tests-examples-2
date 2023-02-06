package ru.yandex.autotests.metrika.beans;

import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.metrika.api.constructor.response.StaticRow;

import java.util.List;

/**
 * Ряд данных в {@link ReportResultInfo} для сравнения drilldown с табличным отчетом
 *
 * @author zgmnkv
 */
public class ReportRowInfo {

    public static ReportRowInfo from(StaticRow tableRow) {
        return new ReportRowInfo(
                tableRow.getDimensions().get(0).get("name"),
                tableRow.getMetrics()
        );
    }

    public static ReportRowInfo from(DrillDownRow drillDownRow) {
        return new ReportRowInfo(
                drillDownRow.getDimension().get("name"),
                drillDownRow.getMetrics()
        );
    }

    private final String dimensionName;
    private final List<Double> metrics;

    public ReportRowInfo(String dimensionName, List<Double> metrics) {
        this.dimensionName = dimensionName;
        this.metrics = metrics;
    }

    @SuppressWarnings("unused")
    public String getDimensionName() {
        return dimensionName;
    }

    @SuppressWarnings("unused")
    public List<Double> getMetrics() {
        return metrics;
    }
}
