package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics;

import java.util.Collection;
import java.util.List;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParametersList;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.EUROPA_PLUS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.IKEA_VSEM;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CDP;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_EXPENSES;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_UPLOADINGS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.WIKIMART_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_EATS_ON_MAPS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_MARKET;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_NEWS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.ATTRIBUTION;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GOAL_ID;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GROUP;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.ADVERTISING;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.EXPENSES_VISITS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.SHARE_SERVICES;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.USER_PARAM;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum.ALL;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addAttributions;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 28.04.2015.
 */
@Features({Requirements.LONG_RUNNING, Requirements.Feature.REPORT})
@Stories({
        Requirements.Story.Report.Type.BYTIME,
        Requirements.Story.Report.Parameter.METRICS,
        Requirements.Story.Report.TOTALS})
@Title("Отчет 'по времени': метрики, итоговые значения")
@RunWith(Parameterized.class)
public class ByTimeTotalsTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule(true);

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = YANDEX_MARKET;
    private static final String START_DATE = "2015-10-20";
    private static final String END_DATE = "2015-10-25";

    private static final Counter SHARE_SERVICES_COUNTER = YANDEX_METRIKA;

    private static final Counter ADVERTISING_COUNTER = IKEA_VSEM;
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

    @Parameter(1)
    public FreeFormParameters tail;

    @Parameters(name = "Метрика {0}")
    public static Collection<Object[]> createParameters() {
        //перебираем метрики
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                user.onMetadataSteps().getMetrics(any()),
                FreeFormParameters::makeParameters)
                //параметры, общие для всех метрик
                .apply(any(), setParameters(
                        new BytimeReportParameters()
                                .withId(COUNTER.get(ID))
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withGroup(ALL)
                                .withAccuracy("1")))
                //для ecommerce свои даты и счетчик
                .apply(ecommerce(), setParameters(
                        new BytimeReportParameters()
                                .withId(ECOMMERCE_TEST)
                                .withDate1(DateConstants.Ecommerce.START_DATE)
                                .withDate2(DateConstants.Ecommerce.END_DATE)
                                .withAccuracy("1")))
                //для РСЯ свои даты и счетчик
                .apply(yan(), setParameters(
                        new BytimeReportParameters()
                                .withId(YANDEX_NEWS)
                                .withDate1(DateConstants.Yan.START_DATE)
                                .withDate2(DateConstants.Yan.END_DATE)
                                .withAccuracy("0.1")))
                .apply(table(SHARE_SERVICES), setParameters(
                        new BytimeReportParameters()
                                .withId(SHARE_SERVICES_COUNTER)))
                .apply(table(ADVERTISING), setParameters(
                        new BytimeReportParameters()
                                .withId(ADVERTISING_COUNTER)
                                .withDate1(ADVERTISING_START_DATE)
                                .withDate2(ADVERTISING_END_DATE)
                                .withDirectClientLogins(
                                        user.onManagementSteps().onClientSteps().getClientLogins(
                                                new ClientsParameters()
                                                        .withCounters(ADVERTISING_COUNTER.get(ID))
                                                        .withDate1(ADVERTISING_START_DATE)
                                                        .withDate2(ADVERTISING_END_DATE),
                                                ulogin(ADVERTISING_COUNTER.get(U_LOGIN))))))
                .apply(table(USER_PARAM), setParameters(
                        new BytimeReportParameters()
                                .withId(USER_PARAM_COUNTER)))
                .apply(table(EXPENSES_VISITS), setParameters(
                        new BytimeReportParameters()
                                .withId(EXPENSE_COUNTER)
                                .withDate1(EXPENSE_START_DATE)
                                .withDate2(EXPENSE_END_DATE)))
                .apply(offlineCalls(), setParameters(
                        new BytimeReportParameters()
                                .withId(COUNTER_OFFLINE_CALLS)
                                .withAccuracy("1")
                                .withDate1(START_DATE_OFFLINE_CALLS)
                                .withDate2(END_DATE_OFFLINE_CALLS)))
                .apply(publishers(), setParameters(
                        new BytimeReportParameters()
                                .withId(COUNTER_PUBLISHERS)
                                .withAccuracy("1")
                                .withDate1(START_DATE_PUBLISHERS)
                                .withDate2(END_DATE_PUBLISHERS)))
                .apply(vacuum(), setParameters(
                        new BytimeReportParameters()
                                .withId(YANDEX_EATS_ON_MAPS)
                                .withAccuracy("1")
                                .withDate1(DateConstants.Vacuum.START_DATE)
                                .withDate2(DateConstants.Vacuum.END_DATE)))
                .apply(cdp(), setParameters(
                        new BytimeReportParameters()
                            .withId(TEST_CDP)
                            .withAccuracy("1")
                            .withDate1(DateConstants.Cdp.START_DATE)
                            .withDate2(DateConstants.Cdp.END_DATE)))
                .apply(crossDeviceAttribution(), setParameters(
                        new BytimeReportParameters()
                                .withId(YANDEX_METRIKA_2_0)
                                .withAccuracy("0.1")
                                .withDate1(DateConstants.CrossDeviceAttribution.START_DATE)
                                .withDate2(DateConstants.CrossDeviceAttribution.END_DATE)))
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
                //размножим по всем периодам группировки
                .apply(parameterized(GROUP), addGroups())
                //расставляем даты и счетчики для некоторых метрик
                .apply(matches(allOf(endsWith("blockedPercentage"), not(startsWith("ym:ev:")))), setParameters(
                        new BytimeReportParameters()
                                .withDate1("2016-04-06")
                                .withDate2("2016-04-16")))
                .apply(matches(equalTo("ym:s:usersPurchasePercentage")), setParameters(
                        new BytimeReportParameters()
                                .withId(ECOMMERCE_TEST)
                                .withDate1(DateConstants.Ecommerce.START_DATE)
                                .withDate2(DateConstants.Ecommerce.END_DATE)))
                .apply(matches(equalTo("ym:s:YMCLIDPercentage")), setParameters(
                        new BytimeReportParameters()
                                .withId(WIKIMART_RU)
                                .withDate1("2016-06-01")
                                .withDate2("2016-06-14")))
                .apply(matches(equalTo("ym:s:YACLIDPercentage")), setParameters(
                        new BytimeReportParameters()
                                .withId(YANDEX_MARKET)
                                .withDate1("2016-06-01")
                                .withDate2("2016-06-14")))
                .apply(matches(equalTo("ym:s:goal<goal_id>bounceRate")), setParameters(goalId(53225L)))
                .apply(parameterized(GOAL_ID).and(matches(anyOf(
                        equalTo("ym:s:goal<goal_id><currency>revenue"),
                        equalTo("ym:s:conversionRateGroup<goal_id>revenue"),
                        equalTo("ym:s:goal<goal_id>revenue")))),
                        setParameters(goalId(SENDFLOWERS_RU)))
                .apply(
                        matches(anyOf(
                                equalTo("ym:s:goal<goal_id><currency>revenue"),
                                equalTo("ym:s:conversionRateGroup<goal_id>revenue"),
                                equalTo("ym:s:goal<goal_id>revenue"))),
                        setParameters(
                                new BytimeReportParameters()
                                        .withDate1(START_DATE)
                                        .withDate2(END_DATE)
                                        .withGroup(ALL)
                                        .withId(SENDFLOWERS_RU)))
                .build(identity());
    }

    @Before
    public void setup() {
        addTestParameter("Метрика", metricName);
        addTestParameter("Остальное", tail.toString());
    }

    @Test
    @IgnoreParametersList({
            @IgnoreParameters(reason = "METR-23460", tag = "pvl")
    })
    public void checkTotalsInReport() {
        StatV1DataBytimeGETSchema result = user.onReportSteps().getBytimeReportAndExpectSuccess(
                tail,
                new CommonReportParameters()
                        .withMetric(metricName));

        assumeThat("массив итоговых значений содержит только одноэлементные массивы (METR-13353)",
                result.getTotals(), everyItem(iterableWithSize(1)));

        List<List<List<Double>>> metrics = user.onResultSteps().getMetrics(result);

        assumeThat("отчет содержит одну строку со значениями метрик", metrics, iterableWithSize(1));

        List<Double> expectedTotals = metrics.get(0).get(0);

        assertThat("итоговые значения совпадают со значениями из единственной строки отчета",
                result.getTotals().get(0), equalTo(expectedTotals));
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()}
        });
    }
}
