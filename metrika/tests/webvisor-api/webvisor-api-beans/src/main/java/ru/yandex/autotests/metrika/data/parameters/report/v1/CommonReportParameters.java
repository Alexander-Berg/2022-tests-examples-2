package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import java.util.Arrays;
import java.util.Collection;

import static ch.lambdaj.collection.LambdaCollections.with;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.joining;
import static org.apache.commons.collections.CollectionUtils.union;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by konkov on 26.09.2014.
 */
public class CommonReportParameters extends AbstractFormParameters {

    public static final String SEPARATOR = ",";

    @FormParameter("id")
    private Long id;

    @FormParameter("ids")
    private String ids;

    @FormParameter("direct_client_ids")
    private String directClientIds;

    @FormParameter("direct_client_logins")
    private String directClientLogins;

    @FormParameter("accuracy")
    private String accuracy;

    @FormParameter("dimensions")
    private String dimensions;

    @FormParameter("filters")
    private String filters;

    @FormParameter("include_undefined")
    private Boolean includeUndefined;

    @FormParameter("lang")
    private String lang;

    @FormParameter("limit")
    private Long limit;

    @FormParameter("offset")
    private Long offset;

    @FormParameter("metrics")
    private String metrics;

    @FormParameter("preset")
    private String preset;

    @FormParameter("sort")
    private String sort;

    @FormParameter("currency")
    private String currency;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setId(Counter counter) {
        setId(counter.get(ID));
    }

    public String getIds() {
        return ids;
    }

    public void setIds(Collection<Counter> counters) {
        this.ids = counters
                .stream()
                .map(c -> c.get(ID).toString())
                .collect(joining(SEPARATOR));
    }

    public void setIds(Counter... counters) {
        this.ids = Arrays.stream(counters)
                .map(c -> c.get(ID).toString())
                .collect(joining(SEPARATOR));
    }

    public void setIds(Long... counters) {
        this.ids = Arrays.stream(counters)
                .map(c -> c.toString())
                .collect(joining(SEPARATOR));
    }

    public String getDirectClientIds() {
        return directClientIds;
    }

    public String getDirectClientLogins() {
        return directClientLogins;
    }

    public void setDirectClientIds(Collection<Long> ids) {
        this.directClientIds = with(ids).join(SEPARATOR);
    }

    public void setDirectClientLogins(Collection<String> logins) {
        this.directClientLogins = with(logins).join(SEPARATOR);
    }

    public void setDirectClientLogins(String login) {
        this.directClientLogins = login;
    }

    public String getAccuracy() {
        return accuracy;
    }

    public void setAccuracy(String accuracy) {
        this.accuracy = accuracy;
    }

    public String getDimensions() {
        return dimensions;
    }

    public void setDimension(String dimension) {
        this.dimensions = dimension;
    }

    public void setDimensions(Collection<String> dimensions) {
        this.dimensions = with(dimensions).join(SEPARATOR);
    }

    public void setDimensions(Collection<String> dimensions, String... additionalDimensions) {
        setDimensions(union(dimensions, asList(additionalDimensions)));
    }

    public void setDimensions(String[] dimensions) {
        setDimensions(asList(dimensions));
    }

    public String getFilters() {
        return filters;
    }

    public void setFilters(String filters) {
        this.filters = filters;
    }

    public Boolean getIncludeUndefined() {
        return includeUndefined;
    }

    public void setIncludeUndefined(Boolean includeUndefined) {
        this.includeUndefined = includeUndefined;
    }

    public void setIncludeUndefined(boolean includeUndefined) {
        setIncludeUndefined(Boolean.valueOf(includeUndefined));
    }

    public String getLang() {
        return lang;
    }

    public void setLang(String lang) {
        this.lang = lang;
    }

    public Long getLimit() {
        return limit;
    }

    public void setLimit(Long limit) {
        this.limit = limit;
    }

    public void setLimit(int limit) {
        setLimit((long) limit);
    }

    public Long getOffset() {
        return offset;
    }

    public void setOffset(Long offset) {
        this.offset = offset;
    }

    public String getMetrics() {
        return metrics;
    }

    public void setMetric(String metric) {
        this.metrics = metric;
    }

    public void setMetrics(Collection<String> metrics) {
        this.metrics = with(metrics).join(SEPARATOR);
    }

    public void setMetrics(String[] metrics) {
        setMetrics(asList(metrics));
    }

    public String getPreset() {
        return preset;
    }

    public void setPreset(String preset) {
        this.preset = preset;
    }

    public String getSort() {
        return sort;
    }

    public void setSort(String sort) {
        this.sort = sort;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public CommonReportParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public CommonReportParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public CommonReportParameters withIds(Collection<Counter> counters) {
        this.setIds(counters);
        return this;
    }

    public CommonReportParameters withIds(Counter... counters) {
        this.setIds(counters);
        return this;
    }

    public CommonReportParameters withIds(Long... counters) {
        this.setIds(counters);
        return this;
    }

    public CommonReportParameters withDirectClientIds(Collection<Long> ids) {
        this.setDirectClientIds(ids);
        return this;
    }

    public CommonReportParameters withDirectClientLogins(Collection<String> logins) {
        this.setDirectClientLogins(logins);
        return this;
    }

    public CommonReportParameters withAccuracy(String accuracy) {
        this.setAccuracy(accuracy);
        return this;
    }

    public CommonReportParameters withDimension(String dimension) {
        this.setDimension(dimension);
        return this;
    }

    public CommonReportParameters withDimension(Collection<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public CommonReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public CommonReportParameters withDimension(Collection<String> dimensions, String... additionalDimensions) {
        this.setDimensions(dimensions, additionalDimensions);
        return this;
    }

    public CommonReportParameters withFilters(String filters) {
        this.setFilters(filters);
        return this;
    }

    public CommonReportParameters withIncludeUndefined(Boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public CommonReportParameters withIncludeUndefined(boolean includeUndefined) {
        this.setIncludeUndefined(includeUndefined);
        return this;
    }

    public CommonReportParameters withLang(String lang) {
        this.setLang(lang);
        return this;
    }

    public CommonReportParameters withLimit(Long limit) {
        this.setLimit(limit);
        return this;
    }

    public CommonReportParameters withLimit(int limit) {
        this.setLimit(limit);
        return this;
    }

    public CommonReportParameters withOffset(Long offset) {
        this.setOffset(offset);
        return this;
    }

    public CommonReportParameters withMetric(String metric) {
        this.setMetric(metric);
        return this;
    }

    public CommonReportParameters withMetrics(String[] metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public CommonReportParameters withMetrics(Collection<String> metrics) {
        this.setMetrics(metrics);
        return this;
    }

    public CommonReportParameters withPreset(String preset) {
        this.setPreset(preset);
        return this;
    }

    public CommonReportParameters withSort(String sort) {
        this.setSort(sort);
        return this;
    }

    public CommonReportParameters withCurrency(String currency) {
        this.currency = currency;
        return this;
    }
}
