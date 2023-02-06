package ru.yandex.autotests.metrika.data.parameters.report.v1.reportorder;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;

import java.util.List;

import static ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters.SEPARATOR;

/**
 * @author zgmnkv
 */
public class ReportOrderByTimeReportParameters extends AbstractFormParameters {

    @FormParameter("top_keys")
    private Integer topKeys;

    @FormParameter("row_ids")
    private String rowIds;

    @FormParameter("metrics")
    private String metrics;

    public Integer getTopKeys() {
        return topKeys;
    }

    public void setTopKeys(Integer topKeys) {
        this.topKeys = topKeys;
    }

    public ReportOrderByTimeReportParameters withTopKeys(Integer topKeys) {
        this.topKeys = topKeys;
        return this;
    }

    public String getRowIds() {
        return rowIds;
    }

    public void setRowIds(String rowIds) {
        this.rowIds = rowIds;
    }

    public void setRowIds(List<List<String>> rowIds) {
        this.rowIds = JsonUtils.toString(rowIds, true);
    }

    public ReportOrderByTimeReportParameters withRowIds(String rowIds) {
        this.rowIds = rowIds;
        return this;
    }

    public ReportOrderByTimeReportParameters withRowIds(List<List<String>> rowIds) {
        setRowIds(rowIds);
        return this;
    }

    public String getMetrics() {
        return metrics;
    }

    public void setMetrics(String metrics) {
        this.metrics = metrics;
    }

    public void setMetrics(List<String> metrics) {
        this.metrics = String.join(SEPARATOR, metrics);
    }

    public ReportOrderByTimeReportParameters withMetrics(String metrics) {
        this.metrics = metrics;
        return this;
    }

    public ReportOrderByTimeReportParameters withMetrics(List<String> metrics) {
        setMetrics(metrics);
        return this;
    }
}
