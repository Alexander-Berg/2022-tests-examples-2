package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.appmetrica.data.Application;

import java.util.List;

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

    public void setParentIds(List<String> parentIds) {
        this.parentId = JsonUtils.toString(parentIds, true);
    }

    public void setParentIds(String[] parentIds) {
        setParentIds(asList(parentIds));
    }

    public DrillDownReportParameters withParentIds(List<String> parentIds) {
        this.setParentIds(parentIds);
        return this;
    }

    public DrillDownReportParameters withParentIds(String[] parentIds) {
        this.setPreset(parentId);
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

    public DrillDownReportParameters withId(Application application) {
        this.setId(application);
        return this;
    }

    public DrillDownReportParameters withIds(List<Application> applications) {
        this.setIds(applications);
        return this;
    }

    public DrillDownReportParameters withIds(Application... applications) {
        this.setIds(applications);
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

    public DrillDownReportParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public DrillDownReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public DrillDownReportParameters withDimensions(List<String> dimensions, String... additionalDimensions) {
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

    public DrillDownReportParameters withMetrics(List<String> metrics) {
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
}
