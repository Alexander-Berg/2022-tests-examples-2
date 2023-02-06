package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.boundary;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.filters.Operator;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by konkov on 07.07.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'таблица': фильтры, не более 100 операндов в одном операторе")
@Issue("METR-16952")
@RunWith(Parameterized.class)
public class TableFiltersMultipleOperandsTest {

    private static final Counter COUNTER = CounterConstants.NO_DATA;
    private static final int MAXIMUM_OPERANDS = 100;
    private static final String DIMENSION_NAME = "ym:s:pageViews";
    private static final String METRIC_NAME = "ym:s:users";

    private static UserSteps user;

    private TableReportParameters reportParameters;

    @Parameterized.Parameter
    public Operator operator;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {Operator.IN},
                {Operator.IN_ALIAS},
                {Operator.NOT_IN},
                {Operator.NOT_IN_ALIAS}
        });
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withDimension(DIMENSION_NAME)
                .withMetric(METRIC_NAME);
    }

    @Test
    public void maximumAllowedOperandsTest() {
        user.onReportSteps().getTableReportAndExpectSuccess(
                reportParameters.withFilters(
                        user.onFilterSteps().getMultiOperandFilter(DIMENSION_NAME, operator, MAXIMUM_OPERANDS)));
    }

    @Test
    public void moreThanMaximumAllowedOperandsTest() {
        user.onReportSteps().getTableReportAndExpectError(
                ReportError.TOO_MANY_VALUES_IN_FILTER,
                reportParameters.withFilters(
                        user.onFilterSteps().getMultiOperandFilter(DIMENSION_NAME, operator, MAXIMUM_OPERANDS + 1)));
    }

}
