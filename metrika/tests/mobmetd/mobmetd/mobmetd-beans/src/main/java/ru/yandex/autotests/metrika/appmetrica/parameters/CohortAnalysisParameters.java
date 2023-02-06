package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.data.Application;

import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;

/**
 * Параметры для КА
 * <p>
 * Created by graev on 09/02/2017.
 */
public final class CohortAnalysisParameters extends CommonFrontParameters {

    @FormParameter("id")
    private Long id;

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("accuracy")
    private String accuracy;

    @FormParameter("cohortType")
    private String cohortType;

    @FormParameter("metric")
    private String metric;

    @FormParameter("retention")
    private String retention;

    @FormParameter("group")
    private String group;

    @FormParameter("conversionType")
    private String conversion;

    @FormParameter("conversionEventName")
    private String conversionEventName;

    @FormParameter("trackerParamKey")
    private String trackerParamKey;

    @FormParameter("currency")
    private String currency;

    @FormParameter("filter")
    private String filter;

    @FormParameter("minCohortSize")
    private Integer minCohortSize;

    public CohortAnalysisParameters() {
    }

    public Long getId() {
        return id;
    }

    public String getDate1() {
        return date1;
    }

    public String getDate2() {
        return date2;
    }

    public String getAccuracy() {
        return accuracy;
    }

    public String getCohortType() {
        return cohortType;
    }

    public String getMetric() {
        return metric;
    }

    public String getRetention() {
        return retention;
    }

    public String getGroup() {
        return group;
    }

    public String getConversion() {
        return conversion;
    }

    public String getConversionEventName() {
        return conversionEventName;
    }

    public String getTrackerParamKey() {
        return trackerParamKey;
    }

    public String getCurrency() {
        return currency;
    }

    public String getFilter() {
        return filter;
    }

    public Integer getMinCohortSize() {
        return minCohortSize;
    }

    public CohortAnalysisParameters withId(Long id) {
        this.id = id;
        return this;
    }

    public CohortAnalysisParameters withId(Application application) {
        this.id = application.get(ID);
        return this;
    }

    public CohortAnalysisParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public CohortAnalysisParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public CohortAnalysisParameters withAccuracy(String accuracy) {
        this.accuracy = accuracy;
        return this;
    }

    public CohortAnalysisParameters withCohortType(CACohortType cohortType) {
        this.cohortType = cohortType.getApiName();
        this.trackerParamKey = cohortType.getUrlParam();
        return this;
    }

    public CohortAnalysisParameters withMetric(CAMetric metric) {
        this.metric = metric.getApiName();
        return this;
    }

    public CohortAnalysisParameters withRetention(CARetention retention) {
        this.retention = retention.getApiName();
        return this;
    }

    public CohortAnalysisParameters withGroup(CAGroup group) {
        this.group = group.getApiName();
        return this;
    }

    public CohortAnalysisParameters withConversion(CAConversion conversion) {
        this.conversion = conversion.getApiName();
        this.conversionEventName = conversion.getEventLabel();
        return this;
    }

    public CohortAnalysisParameters withCurrency(String currency) {
        this.currency = currency;
        return this;
    }

    public CohortAnalysisParameters withFilter(String filter) {
        this.filter = filter;
        return this;
    }

    public CohortAnalysisParameters withMinCohortSize(Integer minCohortSize) {
        this.minCohortSize = minCohortSize;
        return this;
    }
}
