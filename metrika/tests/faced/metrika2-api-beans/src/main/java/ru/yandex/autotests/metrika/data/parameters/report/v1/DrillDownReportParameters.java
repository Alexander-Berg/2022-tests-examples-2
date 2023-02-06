package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import java.util.Collection;

import static java.util.Arrays.asList;

/**
 * Created by okunev on 20.10.2014.
 */
public class DrillDownReportParameters extends TableReportParameters {

    @FormParameter("parentId")
    private String parentId;

    public String getParentId() {
        return parentId;
    }

    public void setParentIds(Collection<String> parentIds) {
        this.parentId = JsonUtils.toString(parentIds, true);
    }

    public void setParentIds(String[] parentIds) {
        setParentIds(asList(parentIds));
    }

    public DrillDownReportParameters withParentIds(Collection<String> parentIds) {
        this.setParentIds(parentIds);
        return this;
    }

    public DrillDownReportParameters withParentIds(String[] parentIds) {
        this.setParentIds(parentIds);
        return this;
    }

    public DrillDownReportParameters withDate1(String date1) {
        this.setDate1(date1);
        return this;
    }

    public DrillDownReportParameters withDate2(String date2) {
        this.setDate2(date2);
        return this;
    }

    public DrillDownReportParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public DrillDownReportParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public DrillDownReportParameters withIds(Collection<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public DrillDownReportParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public DrillDownReportParameters withDirectClientIds(Collection<Long> ids) {
        this.setDirectClientIds(ids);
        return this;
    }

    public DrillDownReportParameters withDirectClientLogins(Collection<String> logins) {
        this.setDirectClientLogins(logins);
        return this;
    }

    public DrillDownReportParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public DrillDownReportParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public DrillDownReportParameters withDimensions(Collection<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public DrillDownReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public DrillDownReportParameters withDimensions(Collection<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public DrillDownReportParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public DrillDownReportParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public DrillDownReportParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public DrillDownReportParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public DrillDownReportParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public DrillDownReportParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public DrillDownReportParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public DrillDownReportParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public DrillDownReportParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public DrillDownReportParameters withMetrics(Collection<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public DrillDownReportParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public DrillDownReportParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }

    public DrillDownReportParameters withConfidence(boolean confidence) {
        this.setConfidence(confidence);
        return this;
    }
}
