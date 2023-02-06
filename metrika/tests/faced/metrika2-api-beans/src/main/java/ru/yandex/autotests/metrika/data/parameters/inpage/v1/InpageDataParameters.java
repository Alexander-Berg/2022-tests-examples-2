package ru.yandex.autotests.metrika.data.parameters.inpage.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;

import java.util.List;

/**
 * Created by okunev on 22.12.2014.
 */
public class InpageDataParameters extends CommonReportParameters {

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("filter")
    private String filter;

    @FormParameter("url")
    private String url;

    @FormParameter("height")
    private String height;

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

    public String getFilter() {
        return filter;
    }

    public void setFilter(String filter) {
        this.filter = filter;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getHeight() {
        return height;
    }

    public void setHeight(String height) {
        this.height = height;
    }

    public InpageDataParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public InpageDataParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public InpageDataParameters withFilter(String filter) {
        this.filter = filter;
        return this;
    }

    public InpageDataParameters withUrl(String url) {
        this.url = url;
        return this;
    }

    public InpageDataParameters withHeight(String height) {
        this.height = height;
        return this;
    }

    public InpageDataParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public InpageDataParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public InpageDataParameters withIds(List<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public InpageDataParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public InpageDataParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public InpageDataParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public InpageDataParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public InpageDataParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public InpageDataParameters withDimensions(List<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public InpageDataParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public InpageDataParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public InpageDataParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public InpageDataParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public InpageDataParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public InpageDataParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public InpageDataParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public InpageDataParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public InpageDataParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public InpageDataParameters withMetrics(List<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public InpageDataParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public InpageDataParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }
}
