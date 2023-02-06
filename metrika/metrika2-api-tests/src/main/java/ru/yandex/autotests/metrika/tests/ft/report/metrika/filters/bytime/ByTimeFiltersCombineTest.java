package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.bytime;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
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
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'по времени': фильтры, совместимость фильтров по метрикам и измерениям")
public class ByTimeFiltersCombineTest {

    private static UserSteps user;

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    private static final String QUERY_METRIC = "ym:s:users";
    private static final String QUERY_DIMENSION = "ym:s:browser";

    private BytimeReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new BytimeReportParameters();
        reportParameters.setId(COUNTER.get(ID));
        reportParameters.setMetric(QUERY_METRIC);
        reportParameters.setDimension(QUERY_DIMENSION);
    }

    @Test
    public void topLevelCombinationAndTest() {
        reportParameters.setFilters(user.onFilterSteps().getTopLevelAndCombination());

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void topLevelCombinationOrTest() {
        reportParameters.setFilters(user.onFilterSteps().getTopLevelOrCombination());

        user.onReportSteps().getBytimeReportAndExpectError(
                ReportError.METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR_WITH_VALUE, reportParameters);
    }

    @Test
    public void allowedNestedCombinationTest() {
        reportParameters.setFilters(user.onFilterSteps().getAllowedNestedCombination());

        user.onReportSteps().getBytimeReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void disallowedNestedCombinationTest() {
        reportParameters.setFilters(user.onFilterSteps().getDisallowedNestedCombination());

        user.onReportSteps().getBytimeReportAndExpectError(
                ReportError.METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR_WITH_VALUE, reportParameters);
    }

}
