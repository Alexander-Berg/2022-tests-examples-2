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
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 17.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.COMPARISON_DRILLDOWN,
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC
})
@Title("Отчет 'сравнение drill down': фильтры, не более 20-ти условий, user-centric")
public class ComparisonDrillDownFiltersNumberOfConditionsUserCentricTest {

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    public static final int CONDITIONS_LIMIT = 20;

    private static UserSteps user;

    private static final String CONDITION_DIMENSION = "ym:s:age";
    private static final String QUERY_METRIC = "ym:s:users";
    private static final String QUERY_DIMENSION = "ym:s:browser";
    private static final String USER_CENTRIC_ATTRIBUTE = "ym:u:gender";
    private static final String USER_ID = "ym:u:userID";

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
    public void maximumConditionsInQuerySegmentA() {
        reportParameters.setFilters_a(
                user.onFilterSteps().getFilterExpressionWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT - 1)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getComparisonDrilldownReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void maximumConditionsInQuerySegmentB() {
        reportParameters.setFilters_b(
                user.onFilterSteps().getFilterExpressionWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT - 1)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getComparisonDrilldownReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumConditionsInQuerySegmentA() {
        reportParameters.setFilters_a(
                user.onFilterSteps().getFilterExpressionWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.TOO_MANY_TERMS_IN_FILTERS, reportParameters);
    }

    @Test
    public void moreThanMaximumConditionsInQuerySegmentB() {
        reportParameters.setFilters_b(
                user.onFilterSteps().getFilterExpressionWithConditions(CONDITION_DIMENSION, CONDITIONS_LIMIT)
                        .and(exists(USER_ID, dimension(USER_CENTRIC_ATTRIBUTE).defined())).build());

        user.onReportSteps().getComparisonDrilldownReportAndExpectError(
                ReportError.TOO_MANY_TERMS_IN_FILTERS, reportParameters);
    }
}
