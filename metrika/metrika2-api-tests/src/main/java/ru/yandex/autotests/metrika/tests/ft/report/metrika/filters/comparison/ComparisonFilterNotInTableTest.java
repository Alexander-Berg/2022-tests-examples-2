package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.comparison;

import org.apache.commons.lang3.StringUtils;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 25.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.COMPARISON, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'сравнение сегментов': фильтры, по метрикам и измерениям из другой таблицы")
public class ComparisonFilterNotInTableTest {
    private static UserSteps user;

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    private static final String CONDITION_VISIT_METRIC = "ym:s:newUsers";
    private static final String CONDITION_VISIT_DIMENSION = "ym:s:endURL";
    private static final String QUERY_VISIT_METRIC = "ym:s:users";
    private static final String QUERY_VISIT_DIMENSION = "ym:s:browser";

    private static final String CONDITION_HIT_METRIC = "ym:pv:users";
    private static final String CONDITION_HIT_DIMENSION = "ym:pv:URL";
    private static final String QUERY_HIT_METRIC = "ym:pv:pageviews";
    private static final String QUERY_HIT_DIMENSION = "ym:pv:browser";

    private ComparisonReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new ComparisonReportParameters();
        reportParameters.setId(COUNTER.get(ID));
    }

    @Test
    public void filterByVisitMetricHitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_a(metric(CONDITION_VISIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_ATTRIBUTE,
                reportParameters);
    }

    @Test
    public void filterByHitMetricVisitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_a(metric(CONDITION_HIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_ATTRIBUTE,
                reportParameters);
    }

    @Test
    public void filterByVisitDimensionVisitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_a(dimension(CONDITION_VISIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByVisitDimensionHitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_a(dimension(CONDITION_VISIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByHitDimensionVisitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_a(dimension(CONDITION_HIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByHitDimensionHitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_a(dimension(CONDITION_HIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByVisitMetricHitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_b(metric(CONDITION_VISIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_ATTRIBUTE,
                reportParameters);
    }

    @Test
    public void filterByHitMetricVisitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_b(metric(CONDITION_HIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_ATTRIBUTE,
                reportParameters);
    }

    @Test
    public void filterByVisitDimensionVisitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_b(dimension(CONDITION_VISIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByVisitDimensionHitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_b(dimension(CONDITION_VISIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByHitDimensionVisitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_b(dimension(CONDITION_HIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByHitDimensionHitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_b(dimension(CONDITION_HIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByVisitMetricVisitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_a(metric(CONDITION_VISIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_A,
                reportParameters);
    }

    @Test
    public void filterByHitMetricHitNamespaceSegmentATest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_a(metric(CONDITION_HIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_A,
                reportParameters);
    }

    @Test
    public void filterByVisitMetricVisitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters_b(metric(CONDITION_VISIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_B,
                reportParameters);
    }

    @Test
    public void filterByHitMetricHitNamespaceSegmentBTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters_b(metric(CONDITION_HIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_B,
                reportParameters);
    }
}
