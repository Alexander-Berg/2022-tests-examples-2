package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.data.Application;

import java.util.List;

/**
 * Created by okunev on 20.10.2014.
 */
public class TableReportParameters extends CommonReportParameters {

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("date_dimension")
    private String dateDimension;

    @FormParameter("funnel_pattern")
    private String funnelPattern;

    @FormParameter("funnel_restriction")
    private String funnelRestriction;

    @FormParameter("segments")
    private String segments;

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

    public String getDateDimension() {
        return dateDimension;
    }

    public void setDateDimension(String dateDimension) {
        this.dateDimension = dateDimension;
    }

    public String getFunnelPattern() {
        return funnelPattern;
    }

    public TableReportParameters withFunnelPattern(String funnelPattern) {
        this.funnelPattern = funnelPattern;
        return this;
    }

    public String getFunnelRestriction() {
        return funnelRestriction;
    }

    public TableReportParameters withFunnelRestriction(String funnelRestriction) {
        this.funnelRestriction = funnelRestriction;
        return this;
    }

    public String getSegments() {
        return segments;
    }

    public TableReportParameters withSegments(String segments) {
        this.segments = segments;
        return this;
    }

    public TableReportParameters withDate1(String date1) {
        this.setDate1(date1);
        return this;
    }

    public TableReportParameters withDate2(String date2) {
        this.setDate2(date2);
        return this;
    }

    public TableReportParameters withDateDimension(String dateDimension) {
        this.setDateDimension(dateDimension);
        return this;
    }

    public TableReportParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public TableReportParameters withId(Application application) {
        this.setId(application);
        return this;
    }

    public TableReportParameters withIds(List<Application> applications) {
        this.setIds(applications);
        return this;
    }

    public TableReportParameters withIds(Application application) {
        this.setIds(application);
        return this;
    }

    public TableReportParameters withIds(Application... applications) {
        this.setIds(applications);
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

    public TableReportParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public TableReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public TableReportParameters withDimensions(List<String> dimensions, String... additionalDimensions) {
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

    public TableReportParameters withMetrics(List<String> metrics) {
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

    public TableReportParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public TableReportParameters withRequestDomain(String requestDomain) {
        this.setRequestDomain(requestDomain);
        return this;
    }
}
