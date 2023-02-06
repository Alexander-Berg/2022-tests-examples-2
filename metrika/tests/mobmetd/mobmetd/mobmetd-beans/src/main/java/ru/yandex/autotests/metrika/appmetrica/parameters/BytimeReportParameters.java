package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.appmetrica.data.Application;

import java.util.List;

/**
 * Created by okunev on 20.10.2014.
 */
public class BytimeReportParameters extends TableReportParameters {

    @FormParameter("group")
    private String group;

    @FormParameter("row_ids")
    private String rowIds;

    @FormParameter("top_keys")
    private String topKeys;

    public String getGroup() {
        return group;
    }

    public void setGroup(String group) {
        this.group = group;
    }

    public void setGroup(GroupEnum group) {
        setGroup(group.getValue());
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

    public String getTopKeys() {
        return topKeys;
    }

    public void setTopKeys(String topKeys) {
        this.topKeys = topKeys;
    }

    public void setTopKeys(int topKeys) {
        this.topKeys = String.valueOf(topKeys);
    }

    public BytimeReportParameters withGroup(final String group) {
        this.group = group;
        return this;
    }

    public BytimeReportParameters withGroup(GroupEnum group) {
        this.group = group.getValue();
        return this;
    }

    public BytimeReportParameters withRowIds(final String rowIds) {
        this.rowIds = rowIds;
        return this;
    }

    public BytimeReportParameters withRowIds(final List<List<String>> rowIds) {
        setRowIds(rowIds);
        return this;
    }

    public BytimeReportParameters withTopKeys(final String topKeys) {
        this.topKeys = topKeys;
        return this;
    }

    public BytimeReportParameters withDate1(String date1) {
        this.setDate1(date1);
        return this;
    }

    public BytimeReportParameters withDate2(String date2) {
        this.setDate2(date2);
        return this;
    }

    public BytimeReportParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public BytimeReportParameters withId(Application application) {
        this.setId(application);
        return this;
    }

    public BytimeReportParameters withIds(List<Application> applications) {
        this.setIds(applications);
        return this;
    }

    public BytimeReportParameters withIds(Application... applications) {
        this.setIds(applications);
        return this;
    }

    public BytimeReportParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public BytimeReportParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public BytimeReportParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public BytimeReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public BytimeReportParameters withDimensions(List<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public BytimeReportParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public BytimeReportParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public BytimeReportParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public BytimeReportParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public BytimeReportParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public BytimeReportParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public BytimeReportParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public BytimeReportParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public BytimeReportParameters withMetrics(List<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public BytimeReportParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public BytimeReportParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }
}
