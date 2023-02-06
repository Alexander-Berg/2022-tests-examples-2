package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.data.Application;

import java.util.Arrays;
import java.util.List;

import static ch.lambdaj.collection.LambdaCollections.with;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.joining;
import static org.apache.commons.collections4.ListUtils.union;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;

/**
 * Created by konkov on 26.09.2014.
 */
public class CommonReportParameters extends CommonFrontParameters {

    public static final String SEPARATOR = ",";

    @FormParameter("id")
    private Long id;

    @FormParameter("ids")
    private String ids;

    @FormParameter("accuracy")
    private String accuracy;

    @FormParameter("proposedAccuracy")
    private Boolean proposedAccuracy;

    @FormParameter("dimensions")
    private String dimensions;

    @FormParameter("filters")
    private String filters;

    @FormParameter("include_undefined")
    private Boolean includeUndefined;

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

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setId(Application application) {
        setId(application.get(ID));
    }

    public String getIds() {
        return ids;
    }

    public void setIds(List<Application> applications) {
        this.ids = applications
                .stream()
                .map(c -> c.get(ID).toString())
                .collect(joining(SEPARATOR));
    }

    public void setIds(Application... applications) {
        this.ids = Arrays.stream(applications)
                .map(c -> c.get(ID).toString())
                .collect(joining(SEPARATOR));
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

    public void setDimensions(List<String> dimensions) {
        this.dimensions = with(dimensions).join(SEPARATOR);
    }

    public void setDimensions(List<String> dimensions, String... additionalDimensions) {
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

    public void setMetrics(List<String> metrics) {
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

    public Boolean getProposedAccuracy() {
        return proposedAccuracy;
    }

    public void setProposedAccuracy(Boolean proposedAccuracy) {
        this.proposedAccuracy = proposedAccuracy;
    }

    public CommonReportParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public CommonReportParameters withId(Application application) {
        this.setId(application);
        return this;
    }

    public CommonReportParameters withIds(List<Application> applications) {
        this.setIds(applications);
        return this;
    }

    public CommonReportParameters withIds(Application... applications) {
        this.setIds(applications);
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

    public CommonReportParameters withDimension(List<String> dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public CommonReportParameters withDimensions(String[] dimensions) {
        this.setDimensions(dimensions);
        return this;
    }

    public CommonReportParameters withDimension(List<String> dimensions, String... additionalDimensions) {
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

    public CommonReportParameters withMetrics(List<String> metrics) {
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

    public CommonReportParameters withProposedAccuracy(boolean proposedAccuracy) {
        this.setProposedAccuracy(proposedAccuracy);
        return this;
    }

}
