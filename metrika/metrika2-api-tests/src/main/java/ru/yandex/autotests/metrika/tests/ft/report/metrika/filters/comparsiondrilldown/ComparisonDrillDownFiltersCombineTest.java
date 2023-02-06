package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.comparsiondrilldown;

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
 * Created by konkov on 11.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.COMPARISON_DRILLDOWN, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'сравнение drill down': фильтры, совместимость фильтров по метрикам и измерениям")
public class ComparisonDrillDownFiltersCombineTest {

    private static UserSteps user;

    private static final Counter COUNTER = CounterConstants.NO_DATA;
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
    public void topLevelCombinationOrSegmentATest() {
        reportParameters.setFilters_a(user.onFilterSteps().getTopLevelOrCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR_WITH_VALUE,
                reportParameters);
    }

    @Test
    public void disallowedNestedCombinationSegmentATest() {
        reportParameters.setFilters_a(user.onFilterSteps().getDisallowedNestedCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR_WITH_VALUE,
                reportParameters);
    }

    @Test
    public void topLevelCombinationOrSegmentBTest() {
        reportParameters.setFilters_b(user.onFilterSteps().getTopLevelOrCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR_WITH_VALUE,
                reportParameters);
    }

    @Test
    public void disallowedNestedCombinationSegmentBTest() {
        reportParameters.setFilters_b(user.onFilterSteps().getDisallowedNestedCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR_WITH_VALUE,
                reportParameters);
    }

    @Test
    public void topLevelCombinationAndSegmentATest() {
        reportParameters.setFilters_a(user.onFilterSteps().getTopLevelAndCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_A,
                reportParameters);
    }

    @Test
    public void disallowedInComparisonDrilldownNestedCombinationSegmentATest() {
        reportParameters.setFilters_a(user.onFilterSteps().getAllowedNestedCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_A,
                reportParameters);
    }

    @Test
    public void topLevelCombinationAndSegmentBTest() {
        reportParameters.setFilters_b(user.onFilterSteps().getTopLevelAndCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_B,
                reportParameters);
    }

    @Test
    public void disallowedInComparisonDrilldownNestedCombinationSegmentBTest() {
        reportParameters.setFilters_b(user.onFilterSteps().getAllowedNestedCombination());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.WRONG_FILTER_SEGMENT_B,
                reportParameters);
    }
}
