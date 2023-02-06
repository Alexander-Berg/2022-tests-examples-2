package ru.yandex.autotests.metrika.data.parameters.analytics.v3;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.apache.commons.collections4.ListUtils.union;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by sourx on 24.03.2016.
 */
public class AnalyticsParameters extends AbstractFormParameters {
    public static final String SEPARATOR = ",";

    @FormParameter("end-date")
    private String endDate;

    @FormParameter("ids")
    private String ids;

    @FormParameter("metrics")
    private String metrics;

    @FormParameter("start-date")
    private String startDate;

    @FormParameter("callback")
    private String callback;

    @FormParameter("dimensions")
    private String dimensions;

    @FormParameter("fields")
    private String fields;

    @FormParameter("filterBraces")
    private String filterBraces;

    @FormParameter("filters")
    private String filters;

    @FormParameter("id")
    private Long id;

    @FormParameter("lang")
    private String lang;

    @FormParameter("max-result")
    private Long maxResult;

    @FormParameter("prettyPrint")
    private Boolean prettyPrint;

    @FormParameter("role")
    private String role;

    @FormParameter("samplingLevel")
    private AnalyticsSampleAccuracyEnum samplingLevel;

    @FormParameter("sort")
    private String sort;

    @FormParameter("start-index")
    private Long startIndex;

    @FormParameter("uid_real")
    private Long uidReal;

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public String getIds() {
        return ids;
    }

    public void setIds(Counter counters) {
        setIds(counters.get(ID));
    }

    public void setIds(Long id) {
        this.ids = "ga:" + id.toString();
    }

    public String getMetrics() {
        return metrics;
    }

    public void setMetrics(String metrics) {
        this.metrics = metrics;
    }

    public void setMetrics(List<String> metrics) {
        this.metrics = metrics.stream().map(Object::toString).collect(Collectors.joining(SEPARATOR));
    }

    public void setMetrics(String[] metrics) {
        setMetrics(asList(metrics));
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getCallback() {
        return callback;
    }

    public void setCallback(String callback) {
        this.callback = callback;
    }

    public String getDimensions() {
        return dimensions;
    }

    public void setDimensions(String dimensions) {
        this.dimensions = dimensions;
    }

    public void setDimensions(List<String> dimensions) {
        this.dimensions = dimensions.stream().map(Object::toString).collect(Collectors.joining(SEPARATOR));
    }

    public void setDimensions(String[] dimensions) {
        setDimensions(asList(dimensions));
    }

    public void setDimensions(List<String> dimensions, String... additionalDimensions) {
        setDimensions(union(dimensions, asList(additionalDimensions)));
    }

    public String getFields() {
        return fields;
    }

    public void setFields(String fields) {
        this.fields = fields;
    }

    public void setFields(List<String> fields) {
        this.fields = fields.stream().map(Object::toString).collect(Collectors.joining(SEPARATOR));
    }

    public void setFields(String[] fields) {
        setFields(asList(fields));
    }

    public String getFilterBraces() {
        return filterBraces;
    }

    public void setFilterBraces(String filterBraces) {
        this.filterBraces = filterBraces;
    }

    public String getFilters() {
        return filters;
    }

    public void setFilters(String filters) {
        this.filters = filters;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getLang() {
        return lang;
    }

    public void setLang(String lang) {
        this.lang = lang;
    }

    public Long getMaxResult() {
        return maxResult;
    }

    public void setMaxResult(Long maxResult) {
        this.maxResult = maxResult;
    }

    public boolean isPrettyPrint() {
        return prettyPrint;
    }

    public void setPrettyPrint(boolean prettyPrint) {
        this.prettyPrint = prettyPrint;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public AnalyticsSampleAccuracyEnum getSamplingLevel() {
        return samplingLevel;
    }

    public void setSamplingLevel(AnalyticsSampleAccuracyEnum samplingLevel) {
        this.samplingLevel = samplingLevel;
    }

    public String getSort() {
        return sort;
    }

    public void setSort(String sort) {
        this.sort = sort;
    }

    public Long getStartIndex() {
        return startIndex;
    }

    public void setStartIndex(Long startIndex) {
        this.startIndex = startIndex;
    }

    public Long getUidReal() {
        return uidReal;
    }

    public void setUidReal(Long uidReal) {
        this.uidReal = uidReal;
    }

    public AnalyticsParameters withEndDate(String endDate) {
        this.setEndDate(endDate);
        return this;
    }

    public AnalyticsParameters withIds(Counter counter) {
        this.setIds(counter);
        return this;
    }

    public AnalyticsParameters withIds(Long id) {
        this.setIds(id);
        return this;
    }

    public AnalyticsParameters withMetrics(String metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public AnalyticsParameters withMetrics(List<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public AnalyticsParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public AnalyticsParameters withStartDate(String startDate) {
        this.setStartDate(startDate);
        return this;
    }

    public AnalyticsParameters withCallback(String callback) {
        this.setCallback(callback);
        return this;
    }

    public AnalyticsParameters withDimensions(String dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public AnalyticsParameters withDimensions(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public AnalyticsParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public AnalyticsParameters withFields(String fields) {
        this.setFields(fields);
        return this;
    }

    public AnalyticsParameters withFilterBraces(String filterBraces) {
        this.setFilterBraces(filterBraces);
        return this;
    }

    public AnalyticsParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public AnalyticsParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public AnalyticsParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public AnalyticsParameters withMaxResult(Long maxResult) {
        this.setMaxResult(maxResult);
        return this;
    }

    public AnalyticsParameters withPrettyPrint(boolean prettyPrint) {
        this.setPrettyPrint(prettyPrint);
        return this;
    }

    public AnalyticsParameters withRole(String role) {
        this.setRole(role);
        return this;
    }

    public AnalyticsParameters withSamplingLevel(AnalyticsSampleAccuracyEnum accuracy) {
        this.setSamplingLevel(accuracy);
        return this;
    }

    public AnalyticsParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }

    public AnalyticsParameters withStartIndex(int startIndex) {
        this.setStartIndex(Long.valueOf(startIndex));
        return this;
    }

    public AnalyticsParameters withUidReal(Long uidReal) {
        this.setUidReal(uidReal);
        return this;
    }
}
