package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics.syntax;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static java.util.function.Function.identity;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DEMOCRAT_SPB;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GROUP;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.QUANTILE;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters.parametrization;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;

/**
 * Мало кто знает, но в метрике уже давно поддерживается вот такая забавная фича.
 * А от написанного теста в ней даже поправились два бага. И один не поправился.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.METRICS})
@Title("Метрики: синтакс ")
@RunWith(Parameterized.class)
public class MetricsSyntaxTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = DEMOCRAT_SPB;
    private static final String START_DATE = "2016-06-20";
    private static final String END_DATE = "2016-06-21";

    private static final String VISIT_DIMENSION_NAME = "ym:s:gender";

    private static final String VISITS_PLUS_1 = "ym:s:visits+1";
    private static final String VISITS_MINUS_1 = "ym:s:visits - 1";
    private static final String VISITS_MUL_1 = "ym:s:visits*1";
    private static final String VISITS_DIV_1 = "ym:s:visits/1";
    private static final String VISITS_DIV_10 = "ym:s:visits/10";
    private static final String VISITS_DIV_10d0 = "ym:s:visits/10.0";
    private static final String VISITS_DIV_M10 = "ym:s:visits/-10.0";
    private static final String SPU = "ym:s:visits/ym:s:users";
    private static final String SPU_VISITS_USERS = "ym:s:visits/ym:s:users,ym:s:visits,ym:s:users";
    private static final String THE_ONE = "ym:s:visits/ym:s:visits";
    private static final String SPU_MUL_100 = "ym:s:visits/ym:s:users*100";
    private static final String SPU_MUL_100_PAREN = "(ym:s:visits/ym:s:users)*100";
    private static final String SPU_MUL_100_PAREN2 = "ym:s:visits/(ym:s:users*100)";
    private static final String SPU_MUL_100_SPACES = "ym:s:visits / ym:s:users * 100";
    private static final String VISITS_MUL_100_ADD_42 = "ym:s:visits * 100 + 42";
    private static final String VISITS_ADD_42_MUL_100 = "ym:s:visits + 42 * 100";
    private static final String MALE_VISITS_RATIO = "ym:s:visits[ym:s:gender=='male']/ym:s:visits[ym:s:gender!=null]";

    @Parameter()
    public String metricName;

    /**
     * Здесь все остальные аргументы вызова API -
     * счетчик, даты, accuracy, параметры параметризованных метрик и измерений
     */
    @Parameter(1)
    public FreeFormParameters tail;

    @Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        //перебираем метрики
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                Arrays.asList(VISITS_PLUS_1, VISITS_MINUS_1, VISITS_MUL_1,
                        VISITS_DIV_1,VISITS_DIV_10,VISITS_DIV_10d0,
                        VISITS_DIV_M10, SPU, SPU_VISITS_USERS, THE_ONE, SPU_MUL_100,
                        SPU_MUL_100_PAREN, SPU_MUL_100_PAREN2, SPU_MUL_100_SPACES,
                        VISITS_MUL_100_ADD_42, VISITS_ADD_42_MUL_100, MALE_VISITS_RATIO),
                FreeFormParameters::makeParameters)
                //параметры общие для всех метрик
                .apply(any(), setParameters(
                        new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withId(COUNTER)))
                //для каждой таблицы (namespace'а) проставляем соответствующую группировку
                .apply(table(VISITS), setParameters(new TableReportParameters().withDimension(VISIT_DIMENSION_NAME)))
                //размножим по всем периодам группировки
                .apply(parameterized(GROUP), addGroups())
                //подставим дефолтный quantile
                .apply(parameterized(QUANTILE), setParameters(parametrization().withQuantile(50)))
                .build(identity());
    }


    @Before
    public void setup() {
        addTestParameter("Метрика", metricName);
        addTestParameter("Остальное", tail.toString());
    }

    @Test
    public void filterSyntaxTest() {
        user.onReportSteps().getTableReportAndExpectSuccess(new CommonReportParameters().withMetric(metricName), tail);
    }

}
