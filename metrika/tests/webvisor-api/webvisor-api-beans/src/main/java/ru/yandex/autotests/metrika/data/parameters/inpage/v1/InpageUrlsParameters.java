package ru.yandex.autotests.metrika.data.parameters.inpage.v1;

import java.util.List;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;

/**
 * Created by okunev on 22.12.2014.
 */
public class InpageUrlsParameters extends CommonReportParameters {

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("per_page")
    private String perPage;

    @FormParameter("table_mode")
    private String tableMode;

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

    public int getPerPage() {
        return Integer.valueOf(perPage);
    }

    public void setPerPage(int perPage) {
        this.perPage = String.valueOf(perPage);
    }

    public String getTableMode() {
        return tableMode;
    }

    public void setTableMode(String tableMode) {
        this.tableMode = tableMode;
    }

    public InpageUrlsParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public InpageUrlsParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public InpageUrlsParameters withPerPage(String perPage) {
        this.perPage = perPage;
        return this;
    }

    public InpageUrlsParameters withTableMode(String tableMode) {
        this.tableMode = tableMode;
        return this;
    }

    public InpageUrlsParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public InpageUrlsParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public InpageUrlsParameters withIds(List<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public InpageUrlsParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public InpageUrlsParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public InpageUrlsParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public InpageUrlsParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public InpageUrlsParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public InpageUrlsParameters withDimensions(List<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public InpageUrlsParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public InpageUrlsParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public InpageUrlsParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public InpageUrlsParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public InpageUrlsParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public InpageUrlsParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public InpageUrlsParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public InpageUrlsParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public InpageUrlsParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public InpageUrlsParameters withMetrics(List<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public InpageUrlsParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public InpageUrlsParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }
}
