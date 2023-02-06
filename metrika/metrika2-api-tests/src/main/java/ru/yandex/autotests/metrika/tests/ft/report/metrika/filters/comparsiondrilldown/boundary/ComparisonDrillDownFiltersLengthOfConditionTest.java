package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.comparsiondrilldown.boundary;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
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
@Stories({Requirements.Story.Report.Type.COMPARISON_DRILLDOWN, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'сравнение drill down': фильтры, не более 10000 символов в строке в одном условии")
public class ComparisonDrillDownFiltersLengthOfConditionTest {

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    private static final int CONDITIONS_LENGTH_LIMIT = 10000;

    private static UserSteps user;

    private static final String CONDITION_DIMENSION = "ym:s:endURL";
    private static final String QUERY_METRIC = "ym:s:users";
    private static final String QUERY_DIMENSION = "ym:s:browser";

    private ComparisonDrilldownReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new ComparisonDrilldownReportParameters();
        reportParameters.setId(COUNTER.get(ID));
        reportParameters.setMetric(QUERY_METRIC);
        reportParameters.setDimension(QUERY_DIMENSION);
    }

    @Test
    public void maximumConditionLengthSegmentA() {
        reportParameters.setFilters_a(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT));

        user.onReportSteps().getComparisonDrilldownReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void maximumConditionLengthSegmentB() {
        reportParameters.setFilters_b(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT));

        user.onReportSteps().getComparisonDrilldownReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumConditionLengthSegmentA() {
        reportParameters.setFilters_a(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT + 1));

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.TOO_LONG_TERMS_IN_FILTERS,
                reportParameters);
    }

    @Test
    public void moreThanMaximumConditionLengthSegmentB() {
        reportParameters.setFilters_b(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT + 1));

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.TOO_LONG_TERMS_IN_FILTERS,
                reportParameters);
    }

}
