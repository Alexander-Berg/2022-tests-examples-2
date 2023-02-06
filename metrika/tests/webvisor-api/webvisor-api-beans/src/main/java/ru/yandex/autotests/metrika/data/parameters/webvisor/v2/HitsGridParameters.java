package ru.yandex.autotests.metrika.data.parameters.webvisor.v2;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import java.util.List;

/**
 * Created by konkov on 09.12.2014.
 */
public class HitsGridParameters extends VisitsGridParameters {

    @FormParameter("visitId")
    private String visitId;

    public String getVisitId() {
        return visitId;
    }

    public void setVisitId(String visitId) {
        this.visitId = visitId;
    }

    public HitsGridParameters withVisitId(String visitId) {
        this.visitId = visitId;
        return this;
    }

    public HitsGridParameters withDate1(String date1) {
        this.setDate1(date1);
        return this;
    }

    public HitsGridParameters withDate2(String date2) {
        this.setDate2(date2);
        return this;
    }

    public HitsGridParameters withIncludeMeta(String includeMeta) {
        this.setIncludeMeta(includeMeta);
        return this;
    }

    public HitsGridParameters withRequestDomain(String requestDomain) {
        this.setRequestDomain(requestDomain);
        return this;
    }

    public HitsGridParameters withSelected(String selected) {
        this.setSelected(selected);
        return this;
    }

    public HitsGridParameters withViewed(String viewed) {
        this.setViewed(viewed);
        return this;
    }

    public HitsGridParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public HitsGridParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public HitsGridParameters withIds(List<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public HitsGridParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public HitsGridParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public HitsGridParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public HitsGridParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public HitsGridParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public HitsGridParameters withDimensions(List<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public HitsGridParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public HitsGridParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public HitsGridParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public HitsGridParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public HitsGridParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public HitsGridParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public HitsGridParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public HitsGridParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public HitsGridParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public HitsGridParameters withMetrics(List<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public HitsGridParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public HitsGridParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }
}
