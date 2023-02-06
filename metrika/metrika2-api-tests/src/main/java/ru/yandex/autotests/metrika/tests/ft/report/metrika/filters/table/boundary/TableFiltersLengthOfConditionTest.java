package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.boundary;

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

/**
 * Created by konkov on 17.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'таблица': фильтры, не более 10000 символов в строке в одном условии")
public class TableFiltersLengthOfConditionTest {

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    private static final int CONDITIONS_LENGTH_LIMIT = 10000;

    private static UserSteps user;

    private static final String CONDITION_DIMENSION = "ym:s:endURL";
    private static final String QUERY_METRIC = "ym:s:users";
    private static final String QUERY_DIMENSION = "ym:s:browser";

    private TableReportParameters reportParameters;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new TableReportParameters();
        reportParameters.setId(COUNTER.get(ID));
        reportParameters.setMetric(QUERY_METRIC);
        reportParameters.setDimension(QUERY_DIMENSION);
    }

    @Test
    public void maximumConditionLength() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT));

        user.onReportSteps().getTableReportAndExpectSuccess(reportParameters);
    }

    @Test
    public void moreThanMaximumConditionLength() {
        reportParameters.setFilters(
                user.onFilterSteps().getFilterWithSingleCondition(CONDITION_DIMENSION, CONDITIONS_LENGTH_LIMIT + 1));

        user.onReportSteps().getTableReportAndExpectError(
                ReportError.TOO_LONG_TERMS_IN_FILTERS,
                reportParameters);
    }
}
