package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table;

import org.apache.commons.lang3.StringUtils;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
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
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'таблица': фильтры, по метрикам и измерениям из другой таблицы")
public class TableFilterNotInTableTest {
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

    private TableReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new TableReportParameters();
        reportParameters.setId(COUNTER.get(ID));
    }

    @Test
    public void filterByVisitMetricVisitNamespaceTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters(metric(CONDITION_VISIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByVisitMetricHitNamespaceTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters(metric(CONDITION_VISIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getTableReportAndExpectError(
                ReportError.WRONG_ATTRIBUTE,
                reportParameters);
    }

    @Test
    public void filterByHitMetricVisitNamespaceTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters(metric(CONDITION_HIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getTableReportAndExpectError(
                ReportError.WRONG_ATTRIBUTE,
                reportParameters);
    }

    @Test
    public void filterByHitMetricHitNamespaceTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters(metric(CONDITION_HIT_METRIC).greaterThan(0).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByVisitDimensionVisitNamespaceTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters(dimension(CONDITION_VISIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByVisitDimensionHitNamespaceTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters(dimension(CONDITION_VISIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByHitDimensionVisitNamespaceTest() {
        reportParameters.setDimension(QUERY_VISIT_DIMENSION);
        reportParameters.setMetric(QUERY_VISIT_METRIC);
        reportParameters.setFilters(dimension(CONDITION_HIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void filterByHitDimensionHitNamespaceTest() {
        reportParameters.setDimension(QUERY_HIT_DIMENSION);
        reportParameters.setMetric(QUERY_HIT_METRIC);
        reportParameters.setFilters(dimension(CONDITION_HIT_DIMENSION).equalTo(StringUtils.EMPTY).build());

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

}
