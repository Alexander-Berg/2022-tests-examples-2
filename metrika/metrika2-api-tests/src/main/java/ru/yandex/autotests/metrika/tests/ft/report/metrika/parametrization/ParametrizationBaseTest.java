package ru.yandex.autotests.metrika.tests.ft.report.metrika.parametrization;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.matchers.SortMatcher.isSortEqualTo;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 27.11.2014.
 */
public abstract class ParametrizationBaseTest {

    private static UserSteps user;
    private static final Counter counter = CounterConstants.LITE_DATA;

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    @Parameterized.Parameter(0)
    public String dimensionName;
    @Parameterized.Parameter(1)
    public String metricName;
    @Parameterized.Parameter(2)
    public String sort;
    @Parameterized.Parameter(3)
    public ParameterValues parametersToReplace;
    @Parameterized.Parameter(4)
    public ParameterValues parametersToRequest;

    private String expectedDimensionName;
    private String expectedMetricName;
    private String expectedSort;

    private StatV1DataGETSchema result;

    protected final static ParameterValues GOAL_ID = new ParameterValues()
            .append(ParametrizationTypeEnum.GOAL_ID, String.valueOf(counter.get(Counter.GOAL_ID)));

    protected final static ParameterValues CURRENCY = new ParameterValues()
            .append(ParametrizationTypeEnum.CURRENCY, "RUB");

    protected final static ParameterValues GOAL_ID_AND_CURRENCY = new ParameterValues()
            .append(GOAL_ID).append(CURRENCY);

    protected final static ParameterValues EMPTY = ParameterValues.EMPTY;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        TableReportParameters reportParameters = new TableReportParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setDate1(START_DATE);
        reportParameters.setDate2(END_DATE);
        reportParameters.setDimension(parametersToReplace.substitute(dimensionName));
        reportParameters.setMetric(parametersToReplace.substitute(metricName));
        reportParameters.setSort(parametersToReplace.substitute(sort));

        expectedDimensionName = parametersToRequest.substitute(reportParameters.getDimensions());
        expectedMetricName = parametersToRequest.substitute(reportParameters.getMetrics());
        expectedSort = parametersToRequest.substitute(reportParameters.getSort());

        result = user.onReportSteps()
                .getTableReportAndExpectSuccess(reportParameters, parametersToRequest.toFormParameters());
    }

    @Test
    public void parametrizationCheckMetric() {
        assertThat("результат содержит ожидаемую метрику", result,
                having(on(StatV1DataGETSchema.class).getQuery().getMetrics(),
                        equalTo(asList(expectedMetricName))));
    }

    @Test
    public void parametrizationCheckDimension() {
        assertThat("результат содержит ожидаемое измерение", result,
                having(on(StatV1DataGETSchema.class).getQuery().getDimensions(),
                        equalTo(asList(expectedDimensionName))));
    }

    @Test
    public void parametrizationCheckSort() {
        assertThat("результат содержит ожидаемую сортировку", result,
                having(on(StatV1DataGETSchema.class).getQuery().getSort(), isSortEqualTo(expectedSort)));
    }
}
