package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.comparison.boundary;

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

/**
 * Created by konkov on 17.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.COMPARISON, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'сравнение сегментов': фильтры, не более 20-ти условий")
public class ComparisonFiltersNumberOfConditionsTest {

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    public static final int CONDITIONS_LIMIT = 20;

    private static UserSteps user;

    private static final String CONDITION_DIMENSION = "ym:s:age";
    private static final String QUERY_METRIC = "ym:s:users";
    private static final String QUERY_DIMENSION = "ym:s:browser";

    private ComparisonReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new ComparisonReportParameters();
        reportParameters.setId(COUNTER.get(ID));
        reportParameters.setMetric(QUERY_METRIC);
        reportParameters.setDimension(QUERY_DIMENSION);
    }

    @Test
    public void maximumConditionsInQuerySegmentA() {
        reportParameters.setFilters_a(
                user.onFilterSteps().getFilterWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT));

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void maximumConditionsInQuerySegmentB() {
        reportParameters.setFilters_b(
                user.onFilterSteps().getFilterWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT));

        user.onReportSteps().getComparisonReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumConditionsInQuerySegmentA() {
        reportParameters.setFilters_a(
                user.onFilterSteps().getFilterWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT + 1));

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.TOO_MANY_TERMS_IN_FILTERS, reportParameters);
    }

    @Test
    public void moreThanMaximumConditionsInQuerySegmentB() {
        reportParameters.setFilters_b(
                user.onFilterSteps().getFilterWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT + 1));

        user.onReportSteps().getComparisonReportAndExpectError(
                ReportError.TOO_MANY_TERMS_IN_FILTERS, reportParameters);
    }
}
