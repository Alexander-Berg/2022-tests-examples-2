package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import java.util.Collection;

import static java.util.Arrays.asList;

/**
 * Created by konkov on 24.10.2014.
 */
public class ComparisonDrilldownReportParameters extends CommonReportParameters {

    @FormParameter("date1_a")
    private String date1_a;

    @FormParameter("date1_b")
    private String date1_b;

    @FormParameter("date2_a")
    private String date2_a;

    @FormParameter("date2_b")
    private String date2_b;

    @FormParameter("filters_a")
    private String filters_a;

    @FormParameter("filters_b")
    private String filters_b;

    @FormParameter("parent_id")
    private String parent_id;

    public String getParent_id() {
        return parent_id;
    }

    public void setParent_id(String parent_id) {
        this.parent_id = parent_id;
    }

    public void setParentIds(Collection<String> parentIds) {
        this.parent_id = JsonUtils.toString(parentIds, true);
    }

    public void setParentIds(String[] parentIds) {
        setParentIds(asList(parentIds));
    }

    public String getDate1_a() {
        return date1_a;
    }

    public void setDate1_a(String date1_a) {
        this.date1_a = date1_a;
    }

    public String getDate1_b() {
        return date1_b;
    }

    public void setDate1_b(String date1_b) {
        this.date1_b = date1_b;
    }

    public String getDate2_a() {
        return date2_a;
    }

    public void setDate2_a(String date2_a) {
        this.date2_a = date2_a;
    }

    public String getDate2_b() {
        return date2_b;
    }

    public void setDate2_b(String date2_b) {
        this.date2_b = date2_b;
    }

    public String getFilters_a() {
        return filters_a;
    }

    public void setFilters_a(String filters_a) {
        this.filters_a = filters_a;
    }

    public String getFilters_b() {
        return filters_b;
    }

    public void setFilters_b(String filters_b) {
        this.filters_b = filters_b;
    }

    public ComparisonDrilldownReportParameters withParent_id(String parent_id) {
        this.parent_id = parent_id;
        return this;
    }

    public ComparisonDrilldownReportParameters withParentIds(Collection<String> parentIds) {
        this.setParentIds(parentIds);
        return this;
    }

    public ComparisonDrilldownReportParameters withParentIds(String[] parentIds) {
        this.setParentIds(parentIds);
        return this;
    }

    public ComparisonDrilldownReportParameters withDate1_a(String date1_a) {
        this.date1_a = date1_a;
        return this;
    }

    public ComparisonDrilldownReportParameters withDate1_b(String date1_b) {
        this.date1_b = date1_b;
        return this;
    }

    public ComparisonDrilldownReportParameters withDate2_a(String date2_a) {
        this.date2_a = date2_a;
        return this;
    }

    public ComparisonDrilldownReportParameters withDate2_b(String date2_b) {
        this.date2_b = date2_b;
        return this;
    }

    public ComparisonDrilldownReportParameters withFilters_a(String filters_a) {
        this.filters_a = filters_a;
        return this;
    }

    public ComparisonDrilldownReportParameters withFilters_b(String filters_b) {
        this.filters_b = filters_b;
        return this;
    }

    public ComparisonDrilldownReportParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public ComparisonDrilldownReportParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public ComparisonDrilldownReportParameters withIds(Collection<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public ComparisonDrilldownReportParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public ComparisonDrilldownReportParameters withDirectClientIds(Collection<Long> ids) {
        this.setDirectClientIds(ids);
        return this;
    }

    public ComparisonDrilldownReportParameters withDirectClientLogins(Collection<String> logins) {
        this.setDirectClientLogins(logins);
        return this;
    }

    public ComparisonDrilldownReportParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public ComparisonDrilldownReportParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public ComparisonDrilldownReportParameters withDimensions(Collection<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public ComparisonDrilldownReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public ComparisonDrilldownReportParameters withDimensions(Collection<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public ComparisonDrilldownReportParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public ComparisonDrilldownReportParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public ComparisonDrilldownReportParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public ComparisonDrilldownReportParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public ComparisonDrilldownReportParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public ComparisonDrilldownReportParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public ComparisonDrilldownReportParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public ComparisonDrilldownReportParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public ComparisonDrilldownReportParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public ComparisonDrilldownReportParameters withMetrics(Collection<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public ComparisonDrilldownReportParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public ComparisonDrilldownReportParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }
}
