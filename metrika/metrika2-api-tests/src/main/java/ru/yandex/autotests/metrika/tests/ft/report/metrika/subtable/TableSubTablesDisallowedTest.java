package ru.yandex.autotests.metrika.tests.ft.report.metrika.subtable;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by konkov on 17.04.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.SUB_TABLES})
@Title("Отчет 'таблица': не допустимые подтаблицы")
@RunWith(Parameterized.class)
public class TableSubTablesDisallowedTest {

    private UserSteps user;

    private static final Counter COUNTER = CounterConstants.NO_DATA;

    private static final String METRIC_VISITS = "ym:s:flashEnabledPercentage";
    private static final String PARSED_PARAMS_DIMENSION_VISITS = "ym:s:paramsLevel1";

    private static final String GOALS_DIMENSION_VISITS = "ym:s:goal";

    private static final String INTEREST_DIMENSION_VISITS = "ym:s:interest";

    private static final String EACTION_DIMENSION = "ym:s:productName";
    private static final String EACTION_METRIC = "ym:s:productPurchasedPrice";

    private static final String EPURCHASE_DIMENSION = "ym:s:purchaseID";
    private static final String EPURCHASE_METRIC = "ym:s:ecommercePurchases";

    @Parameterized.Parameter(0)
    public List<String> dimensionNames;

    @Parameterized.Parameter(1)
    public List<String> metricNames;

    @Parameterized.Parameters(name = "dimensions: {0}, metrics: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                //2 subtables
                {asList(PARSED_PARAMS_DIMENSION_VISITS, GOALS_DIMENSION_VISITS), asList(METRIC_VISITS)},
                {asList(PARSED_PARAMS_DIMENSION_VISITS, INTEREST_DIMENSION_VISITS), asList(METRIC_VISITS)},
                {asList(GOALS_DIMENSION_VISITS, INTEREST_DIMENSION_VISITS), asList(METRIC_VISITS)},

                {asList(EACTION_DIMENSION, GOALS_DIMENSION_VISITS), asList(EACTION_METRIC)},
                {asList(EACTION_DIMENSION, PARSED_PARAMS_DIMENSION_VISITS), asList(EACTION_METRIC)},
                {asList(EACTION_DIMENSION, INTEREST_DIMENSION_VISITS), asList(EACTION_METRIC)},

                {asList(EPURCHASE_DIMENSION, GOALS_DIMENSION_VISITS), asList(EPURCHASE_METRIC)},
                {asList(EPURCHASE_DIMENSION, PARSED_PARAMS_DIMENSION_VISITS), asList(EPURCHASE_METRIC)},
                {asList(EPURCHASE_DIMENSION, INTEREST_DIMENSION_VISITS), asList(EPURCHASE_METRIC)},

                {asList(EACTION_DIMENSION, EPURCHASE_DIMENSION), asList(METRIC_VISITS)},

                //3 subtables
                {asList(PARSED_PARAMS_DIMENSION_VISITS, GOALS_DIMENSION_VISITS, INTEREST_DIMENSION_VISITS),
                        asList(METRIC_VISITS)},

                {asList(EACTION_DIMENSION, EPURCHASE_DIMENSION, PARSED_PARAMS_DIMENSION_VISITS),
                        asList(METRIC_VISITS)},
                {asList(EACTION_DIMENSION, EPURCHASE_DIMENSION, GOALS_DIMENSION_VISITS), asList(METRIC_VISITS)},
                {asList(EACTION_DIMENSION, EPURCHASE_DIMENSION, INTEREST_DIMENSION_VISITS), asList(METRIC_VISITS)},
        });
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Test
    public void subTablesShouldBeDisallowed() {
        user.onReportSteps().getTableReportAndExpectError(ReportError.MULTIPLE_DATESETS_NOT_ALLOWED,
                new TableReportParameters()
                        .withId(COUNTER.get(ID))
                        .withDimensions(dimensionNames)
                        .withMetrics(metricNames));
    }
}
