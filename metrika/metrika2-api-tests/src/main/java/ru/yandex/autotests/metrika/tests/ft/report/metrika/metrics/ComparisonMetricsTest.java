package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataComparisonGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.*;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters.parametrization;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasMetricValues;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;
import static ru.yandex.autotests.metrika.utils.Utils.flatten;

/**
 * Created by konkov on 16.12.2014.
 */
@Features({Requirements.LONG_RUNNING, Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.Type.COMPARISON, Requirements.Story.Report.Parameter.METRICS})
@Title("Отчет 'сравнение сегментов': метрики")
@RunWith(Parameterized.class)
public class ComparisonMetricsTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    /**
     * user и counter инициализируются статически, т.к. они используются на этапе
     * формирования перечня параметров теста
     */
    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = YANDEX_MARKET;
    private static final String START_DATE = "2015-06-20";
    private static final String END_DATE = "2015-06-21";

    private static final Counter SHARE_SERVICES_COUNTER = YANDEX_METRIKA;

    private static final String VISIT_DIMENSION_NAME = "ym:s:gender";
    private static final String VISIT_ECOMMERCE_DIMENSION_NAME = "ym:s:date";
    private static final String HIT_DIMENSION_NAME = "ym:pv:gender";
    private static final String SHARE_SERVICES_DIMENSION_NAME = "ym:sh:gender";
    private static final String SITE_SPEED_DIMENSION_NAME = "ym:sp:gender";
    private static final String EXTERNAL_LINKS_DIMENSION_NAME = "ym:el:gender";
    private static final String DOWNLOADS_DIMENSION_NAME = "ym:dl:gender";
    private static final String ADVERTISING_DIMENSION_NAME = "ym:ad:gender";
    private static final String USER_PARAM_DIMENSION_NAME = "ym:up:paramsLevel1";
    private static final String EXPENSE_DIMENSION_NAME = "ym:ev:<attribution>ExpenseSource";

    private static final Counter ADVERTISING_COUNTER = DRESSTOP;
    private static final String ADVERTISING_START_DATE = DateConstants.Advertising.START_DATE;
    private static final String ADVERTISING_END_DATE = DateConstants.Advertising.END_DATE;

    private static final Counter USER_PARAM_COUNTER = YANDEX_METRIKA_2_0;

    private static final Counter COUNTER_OFFLINE_CALLS = TEST_UPLOADINGS;
    private static final String START_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.START_DATE;
    private static final String END_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.END_DATE;

    private static final Counter COUNTER_PUBLISHERS = EUROPA_PLUS;
    private static final String START_DATE_PUBLISHERS = DateConstants.Publishers.START_DATE;
    private static final String END_DATE_PUBLISHERS = DateConstants.Publishers.END_DATE;

    private static final Counter EXPENSE_COUNTER = TEST_EXPENSES;
    private static final String EXPENSE_START_DATE = DateConstants.Expense.START_DATE;
    private static final String EXPENSE_END_DATE = DateConstants.Expense.END_DATE;


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
                user.onMetadataSteps().getMetrics(any()),
                FreeFormParameters::makeParameters)
                //параметры общие для всех метрик
                .apply(table(USER_PARAM).negate(), setParameters(
                        new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate1_b(END_DATE)
                                .withDate2_a(START_DATE)
                                .withDate2_b(END_DATE)
                                .withId(COUNTER)))
                //для каждой таблицы (namespace'а) проставляем соответствующую группировку
                .apply(table(HITS), setParameters(new ComparisonReportParameters().withDimension(HIT_DIMENSION_NAME)))
                .apply(table(VISITS), setParameters(new ComparisonReportParameters().withDimension(VISIT_DIMENSION_NAME)))
                //для ecommerce свои даты и счетчик
                .apply(ecommerce(), setParameters(
                        new ComparisonReportParameters()
                                .withId(ECOMMERCE_TEST)
                                .withDimension(VISIT_ECOMMERCE_DIMENSION_NAME)
                                .withDate1_a(DateConstants.Ecommerce.START_DATE)
                                .withDate2_a(DateConstants.Ecommerce.END_DATE)
                                .withDate1_b(DateConstants.Ecommerce.START_DATE)
                                .withDate2_b(DateConstants.Ecommerce.END_DATE)
                                .withAccuracy("1")))
                //для РСЯ свои даты и счетчик
                .apply(yan(), setParameters(
                        new ComparisonReportParameters()
                                .withId(YANDEX_NEWS)
                                .withDimension(VISIT_DIMENSION_NAME)
                                .withDate1_a(DateConstants.Yan.START_DATE)
                                .withDate2_a(DateConstants.Yan.END_DATE)
                                .withDate1_b(DateConstants.Yan.START_DATE)
                                .withDate2_b(DateConstants.Yan.END_DATE)
                                .withAccuracy("0.1")))
                .apply(table(SITE_SPEED), setParameters(new ComparisonReportParameters().withDimension(SITE_SPEED_DIMENSION_NAME)))
                .apply(table(SHARE_SERVICES), setParameters(
                        new ComparisonReportParameters()
                                .withId(SHARE_SERVICES_COUNTER)
                                .withDimension(SHARE_SERVICES_DIMENSION_NAME)
                                .withAccuracy("1")))
                .apply(table(EXTERNAL_LINKS), setParameters(new ComparisonReportParameters().withDimension(EXTERNAL_LINKS_DIMENSION_NAME)))
                .apply(table(DOWNLOADS), setParameters(new ComparisonReportParameters().withDimension(DOWNLOADS_DIMENSION_NAME)))
                .apply(table(ADVERTISING), setParameters(
                        new ComparisonReportParameters()
                                .withId(ADVERTISING_COUNTER)
                                .withDimension(ADVERTISING_DIMENSION_NAME)
                                .withDate1_a(ADVERTISING_START_DATE)
                                .withDate2_a(ADVERTISING_END_DATE)
                                .withDate1_b(ADVERTISING_START_DATE)
                                .withDate2_b(ADVERTISING_END_DATE)
                                .withDirectClientLogins(
                                        user.onManagementSteps().onClientSteps().getClientLogins(
                                                new ClientsParameters()
                                                        .withCounters(ADVERTISING_COUNTER.get(ID))
                                                        .withDate1(ADVERTISING_START_DATE)
                                                        .withDate2(ADVERTISING_END_DATE),
                                                ulogin(ADVERTISING_COUNTER.get(U_LOGIN))))))
                .apply(table(USER_PARAM), setParameters(
                        new ComparisonReportParameters()
                                .withId(USER_PARAM_COUNTER)
                                .withDimension(USER_PARAM_DIMENSION_NAME)))
                .apply(table(EXPENSES_VISITS), setParameters(
                        new ComparisonReportParameters()
                                .withId(EXPENSE_COUNTER)
                                .withDate1_a(EXPENSE_START_DATE)
                                .withDate2_a(EXPENSE_END_DATE)
                                .withDate1_b(EXPENSE_START_DATE)
                                .withDate2_b(EXPENSE_END_DATE)
                                .withDimension(EXPENSE_DIMENSION_NAME)))
                .apply(offlineCalls(), setParameters(
                        new ComparisonReportParameters()
                                .withId(COUNTER_OFFLINE_CALLS)
                                .withAccuracy("1")
                                .withDate1_a(START_DATE_OFFLINE_CALLS)
                                .withDate2_a(END_DATE_OFFLINE_CALLS)
                                .withDate1_b(START_DATE_OFFLINE_CALLS)
                                .withDate2_b(END_DATE_OFFLINE_CALLS)))
                .apply(publishers(), setParameters(
                        new ComparisonReportParameters()
                                .withId(COUNTER_PUBLISHERS)
                                .withAccuracy("1")
                                .withDate1_a(START_DATE_PUBLISHERS)
                                .withDate2_a(END_DATE_PUBLISHERS)
                                .withDate1_b(START_DATE_PUBLISHERS)
                                .withDate2_b(END_DATE_PUBLISHERS)))
                .apply(vacuum(), setParameters(
                        new ComparisonReportParameters()
                                .withId(YANDEX_EATS_ON_MAPS)
                                .withAccuracy("1")
                                .withDate1_a(DateConstants.Vacuum.START_DATE)
                                .withDate2_a(DateConstants.Vacuum.END_DATE)
                                .withDate1_b(DateConstants.Vacuum.START_DATE)
                                .withDate2_b(DateConstants.Vacuum.END_DATE)))
                .apply(recommendationWidget(), setParameters(
                        new ComparisonReportParameters()
                                .withId(YANDEX_WEATHER)
                                .withAccuracy("0.001")
                                .withDate1_a(DateConstants.RecommendationWidget.START_DATE)
                                .withDate2_a(DateConstants.RecommendationWidget.END_DATE)
                                .withDate1_b(DateConstants.RecommendationWidget.START_DATE)
                                .withDate2_b(DateConstants.RecommendationWidget.END_DATE)))
                .apply(cdp(), setParameters(
                        new ComparisonReportParameters()
                                .withId(TEST_CDP)
                                .withAccuracy("1")
                                .withDate1_a(DateConstants.Cdp.START_DATE)
                                .withDate2_a(DateConstants.Cdp.END_DATE)
                                .withDate1_b(DateConstants.Cdp.START_DATE)
                                .withDate2_b(DateConstants.Cdp.END_DATE)))
                .apply(crossDeviceAttribution(), setParameters(
                        new ComparisonReportParameters()
                                .withId(YANDEX_METRIKA_2_0)
                                .withAccuracy("0.1")
                                .withDate1_a(DateConstants.CrossDeviceAttribution.START_DATE)
                                .withDate2_a(DateConstants.CrossDeviceAttribution.END_DATE)
                                .withDate1_b(DateConstants.CrossDeviceAttribution.START_DATE)
                                .withDate2_b(DateConstants.CrossDeviceAttribution.END_DATE)))
                //подставим goal_id
                .apply(parameterized(GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(GOAL_ID).and(ecommerce()),
                        setParameters(goalId(ECOMMERCE_TEST)))
                .apply(table(ADVERTISING).and(parameterized(GOAL_ID)),
                        setParameters(goalId(ADVERTISING_COUNTER)))
                .apply(table(EXPENSES_VISITS).and(parameterized(GOAL_ID)),
                        setParameters(goalId(EXPENSE_COUNTER)))
                //размножим по всем атрибуциям
                .apply(parameterized(ATTRIBUTION), addAttributions())
                //размножим по всем валютам
                .apply(parameterized(CURRENCY), addCurrencies())
                //размножим по всем периодам группировки
                .apply(parameterized(GROUP), addGroups())
                //подставим дефолтный quantile
                .apply(parameterized(QUANTILE), setParameters(parametrization().withQuantile(50)))
                .build(identity());
    }

    private StatV1DataComparisonGETSchema result;

    @Before
    public void setup() {
        addTestParameter("Метрика", metricName);
        addTestParameter("Остальное", tail.toString());
        result = user.onReportSteps().getComparisonReportAndExpectSuccess(
                tail,
                new CommonReportParameters()
                        .withMetric(metricName));
    }

    @Test
    @IgnoreParameters(reason = "METR-23460", tag = "pvl")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkMetricValues() {
        //для проверки корректности значений метрик извлекаем их в линейный список
        List<Double> metrics = flatten(user.onResultSteps().getMetrics(result));

        assumeThat("значения метрик присутствуют", metrics, not(empty()));

        assertThat("все значения метрик числа либо null", metrics, iterableHasMetricValues());
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()}
        });
    }

    @IgnoreParameters.Tag(name = "adfox")
    public static Collection<Object[]> ignoreParametersAdfox() {
        return asList(new Object[][]{
                {containsString("adfox"), anything()}
        });
    }
}
