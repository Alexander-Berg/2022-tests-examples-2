package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics.syntax;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DEMOCRAT_SPB;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;

/**
 * Created by konkov on 20.08.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.METRICS})
@Title("Метрики: синтакс (негативные)")
@RunWith(Parameterized.class)
public class MetricsSyntaxNegativeTest {

    /**
     * user и counter инициализируются статически, т.к. они используются на этапе
     * формирования перечня параметров теста
     */
    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = DEMOCRAT_SPB;
    private static final String START_DATE = "2016-06-20";
    private static final String END_DATE = "2016-06-21";

    private static final String VISIT_DIMENSION_NAME = "ym:s:gender";

    private static final String METRIC_LIST_WITH_COMMA = "ym:s:visits,";
    /* разбор этой метрики падает, т.к. в апи токенизатор цепляет знак минуса к литералу 1 и ast по двум токенам потом не строится.
    * нельзя сказать что это во-первых разумное поведение, во-вторых стоит специфицирования в виде тестов на будущее,
    * но исправлять сейчас вроде как незачем и для документации можно оставить. */
    private static final String VISITS_MINUS_1 = "ym:s:visits-1";
    private static final String VISITS_QUOTAS = "'ym:s:visits'";

    @Parameter()
    public String metricName;

    /**
     * Здесь все остальные аргументы вызова API -
     * счетчик, даты, accuracy, параметры параметризованных метрик и измерений
     */
    @Parameter(1)
    public FreeFormParameters tail;

    @Parameter(2)
    public ReportError error;

    @Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        FreeFormParameters parameters = new FreeFormParameters().append(new TableReportParameters()
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withId(COUNTER)
                .withDimension(VISIT_DIMENSION_NAME)
        );
        return Arrays.<Object[]>asList(
                new Object[]{METRIC_LIST_WITH_COMMA, parameters, ReportError.WRONG_EXPRESSION},
                new Object[]{VISITS_MINUS_1, parameters, ReportError.WRONG_EXPRESSION},
                new Object[]{VISITS_QUOTAS, parameters, ReportError.WRONG_METRIC}
        );
    }


    @Before
    public void setup() {
        addTestParameter("Метрика", metricName);
        addTestParameter("Остальное", tail.toString());
    }

    @Test
    public void filterSyntaxTest() {
        user.onReportSteps().getTableReportAndExpectError(error,
                tail, new CommonReportParameters().withMetric(metricName));
    }

}
