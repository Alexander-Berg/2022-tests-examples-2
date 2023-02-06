package ru.yandex.autotests.metrika.tests.ft.report.metrika.parametrization;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by konkov on 28.11.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.PARAMETRIZATION})
@Title("Негативные тесты параметризации")
@RunWith(Parameterized.class)
public class NegativeParametrizationTest {

    private static UserSteps user;
    private static final Counter counter = CounterConstants.NO_DATA;

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    private static final Long CODE = 400L;
    private static final String MESSAGE_WRONG_SORT = "Wrong sort, value: ym:s:goal<goal_id>reaches, code: 4004";
    private static final String MESSAGE_MISSING_PARAMETER = "Parameter goal_id not provided";

    @Parameterized.Parameter(0)
    public String dimensionName;
    @Parameterized.Parameter(1)
    public String metricName;
    @Parameterized.Parameter(2)
    public String sort;
    @Parameterized.Parameter(3)
    public ParameterValues parametersToRequest;
    @Parameterized.Parameter(4)
    public String message;

    private TableReportParameters reportParameters;

    private final static ParameterValues GOAL_ID = new ParameterValues()
            .append(ParametrizationTypeEnum.GOAL_ID, String.valueOf(counter.get(Counter.GOAL_ID)));

    private final static ParameterValues CURRENCY = new ParameterValues()
            .append(ParametrizationTypeEnum.CURRENCY, "RUB");

    private final static ParameterValues EMPTY = ParameterValues.EMPTY;

    private static final String DIMENSION = "ym:s:browser";
    private static final String METRIC = "ym:s:users";
    private static final String PARAM_DIM = "ym:s:goal<goal_id>IsReached";
    private static final String PARAM_METRIC = "ym:s:goal<goal_id>reaches";
    private static final String TWO_PARAM_METRIC = "ym:s:goal<goal_id><currency>AdCostPerVisit";

    @Parameterized.Parameters(name = "{0} {1} {2} {3}")
    public static Collection createParameters() {
        return asList(new Object[][]{
                {PARAM_DIM, METRIC, METRIC, EMPTY, MESSAGE_MISSING_PARAMETER},
                {DIMENSION, PARAM_METRIC, DIMENSION, EMPTY, MESSAGE_MISSING_PARAMETER},
                {DIMENSION, GOAL_ID.substitute(PARAM_METRIC), PARAM_METRIC, EMPTY, MESSAGE_MISSING_PARAMETER},
                {DIMENSION, TWO_PARAM_METRIC, DIMENSION, EMPTY, MESSAGE_MISSING_PARAMETER},
                {DIMENSION, TWO_PARAM_METRIC, DIMENSION, CURRENCY, MESSAGE_MISSING_PARAMETER},
                {DIMENSION, CURRENCY.substitute(TWO_PARAM_METRIC), DIMENSION, EMPTY, MESSAGE_MISSING_PARAMETER},
        });
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        reportParameters = new TableReportParameters()
                .withId(counter.get(ID))
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withDimension(dimensionName)
                .withMetric(metricName)
                .withSort(sort);
    }

    @Test
    public void parametrizationErrorTest() {
        user.onReportSteps().getTableReportAndExpectError(CODE, message,
                reportParameters, parametersToRequest.toFormParameters());
    }
}
