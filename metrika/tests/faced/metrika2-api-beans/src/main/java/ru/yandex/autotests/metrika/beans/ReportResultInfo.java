package ru.yandex.autotests.metrika.beans;

import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Основные данные из отчета, необходимые для сравнения drilldown с табличным отчетом
 *
 * @author zgmnkv
 */
public class ReportResultInfo {

    public static ReportResultInfo from(StatV1DataGETSchema tableResult) {
        return new ReportResultInfo(
                tableResult.getTotalRows(),
                tableResult.getTotals(),
                tableResult.getData().stream()
                        .map(ReportRowInfo::from)
                        .collect(Collectors.toList())
        );
    }

    public static ReportResultInfo from(StatV1DataDrilldownGETSchema drillDownResult) {
        return new ReportResultInfo(
                drillDownResult.getTotalRows(),
                drillDownResult.getTotals(),
                drillDownResult.getData().stream()
                        .map(ReportRowInfo::from)
                        .collect(Collectors.toList())
        );
    }

    private final Long totalRows;
    private final List<Double> totals;
    private final List<ReportRowInfo> data;

    public ReportResultInfo(Long totalRows, List<Double> totals, List<ReportRowInfo> data) {
        this.totalRows = totalRows;
        this.totals = totals;
        this.data = data;
    }

    @SuppressWarnings("unused")
    public Long getTotalRows() {
        return totalRows;
    }

    @SuppressWarnings("unused")
    public List<Double> getTotals() {
        return totals;
    }

    @SuppressWarnings("unused")
    public List<ReportRowInfo> getData() {
        return data;
    }
}
