package ru.yandex.autotests.metrika.data.parameters.webvisor.v2;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;

import java.util.List;

/**
 * Created by konkov on 09.12.2014.
 */
public class VisitsGridParameters extends CommonReportParameters {

    @FormParameter("date1")
    private String date1 = "3daysAgo";

    @FormParameter("date2")
    private String date2 = "2daysAgo";

    @FormParameter("include_meta")
    private String includeMeta = "false";

    @FormParameter("request_domain")
    private String requestDomain;

    @FormParameter("selected")
    private String selected;

    @FormParameter("viewed")
    private String viewed;

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

    public String getIncludeMeta() {
        return includeMeta;
    }

    public void setIncludeMeta(String includeMeta) {
        this.includeMeta = includeMeta;
    }

    public String getRequestDomain() {
        return requestDomain;
    }

    public void setRequestDomain(String requestDomain) {
        this.requestDomain = requestDomain;
    }

    public String getSelected() {
        return selected;
    }

    public void setSelected(String selected) {
        this.selected = selected;
    }

    public String getViewed() {
        return viewed;
    }

    public void setViewed(String viewed) {
        this.viewed = viewed;
    }

    public VisitsGridParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public VisitsGridParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public VisitsGridParameters withIncludeMeta(String includeMeta) {
        this.includeMeta = includeMeta;
        return this;
    }

    public VisitsGridParameters withRequestDomain(String requestDomain) {
        this.requestDomain = requestDomain;
        return this;
    }

    public VisitsGridParameters withSelected(String selected) {
        this.selected = selected;
        return this;
    }

    public VisitsGridParameters withViewed(String viewed) {
        this.viewed = viewed;
        return this;
    }

    public VisitsGridParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public VisitsGridParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public VisitsGridParameters withIds(List<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public VisitsGridParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public VisitsGridParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public VisitsGridParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public VisitsGridParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public VisitsGridParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public VisitsGridParameters withDimensions(List<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public VisitsGridParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public VisitsGridParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public VisitsGridParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public VisitsGridParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public VisitsGridParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public VisitsGridParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public VisitsGridParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public VisitsGridParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public VisitsGridParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public VisitsGridParameters withMetrics(List<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public VisitsGridParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public VisitsGridParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }
}
