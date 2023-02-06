package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import java.util.Collection;

/**
 * Created by okunev on 20.10.2014.
 */
public class TableReportParameters extends CommonReportParameters {

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("with_confidence")
    private Boolean confidence;

    public String getDate1() {
        return date1;
    }

    public void setDate1(String date1) {
        this.date1 = date1;
    }

    public String getDate2() {
        return date2;
    }

    public void setDate2(String date2) {
        this.date2 = date2;
    }

    public TableReportParameters withDate1(String date1) {
        this.setDate1(date1);
        return this;
    }

    public TableReportParameters withDate2(String date2) {
        this.setDate2(date2);
        return this;
    }

    public TableReportParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public TableReportParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public TableReportParameters withIds(Collection<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public TableReportParameters withIds(Counter counters) {
        this.setIds(counters);
        return this;
    }

    public TableReportParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public TableReportParameters withDirectClientIds(Collection<Long> ids) {
        this.setDirectClientIds(ids);
        return this;
    }

    public TableReportParameters withDirectClientLogins(Collection<String> logins) {
        this.setDirectClientLogins(logins);
        return this;
    }

    public TableReportParameters withDirectClientLogins(String login) {
        this.setDirectClientLogins(login);
        return this;
    }

    public TableReportParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public TableReportParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public TableReportParameters withDimensions(Collection<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public TableReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public TableReportParameters withDimensions(Collection<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public TableReportParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public TableReportParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public TableReportParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public TableReportParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public TableReportParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public TableReportParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public TableReportParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public TableReportParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public TableReportParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public TableReportParameters withMetrics(Collection<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public TableReportParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public TableReportParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }

    public boolean isConfidence() {
        return confidence;
    }

    public TableReportParameters withConfidence(boolean confidence) {
        this.confidence = confidence;
        return this;
    }

    public void setConfidence(boolean confidence) {
        this.confidence = confidence;
    }
}
