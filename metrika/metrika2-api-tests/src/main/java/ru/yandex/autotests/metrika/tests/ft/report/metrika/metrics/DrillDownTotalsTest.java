package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.commons.rules.IgnoreParameters.Tag;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.*;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Term.metric;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;

/**
 * Created by konkov on 28.04.2015.
 */
@Features({Requirements.LONG_RUNNING, Requirements.Feature.REPORT})
@Stories({
        Requirements.Story.Report.Type.DRILLDOWN,
        Requirements.Story.Report.Parameter.METRICS,
        Requirements.Story.Report.TOTALS})
@Title("Отчет 'drill down': метрики, итоговые значения")
@RunWith(Parameterized.class)
public class DrillDownTotalsTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule(false);

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
                        new DrillDownReportParameters()
                                .withId(COUNTER.get(ID))
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withAccuracy("1")))
                //для ecommerce свои даты и счетчик
                .apply(ecommerce(), setParameters(
                        new DrillDownReportParameters()
                                .withId(ECOMMERCE_TEST)
                                .withDate1(DateConstants.Ecommerce.START_DATE)
                                .withDate2(DateConstants.Ecommerce.END_DATE)
                                .withAccuracy("1")))
                //для РСЯ свои даты и счетчик
                .apply(yan(), setParameters(
                        new DrillDownReportParameters()
                                .withId(YANDEX_NEWS)
                                .withDate1(DateConstants.Yan.START_DATE)
                                .withDate2(DateConstants.Yan.END_DATE)
                                .withAccuracy("0.1")))
                .apply(table(SHARE_SERVICES), setParameters(
                        new DrillDownReportParameters()
                                .withId(SHARE_SERVICES_COUNTER)))
                .apply(table(ADVERTISING), setParameters(
                        new DrillDownReportParameters()
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
                        new DrillDownReportParameters()
                                .withId(USER_PARAM_COUNTER)))
                .apply(table(EXPENSES_VISITS), setParameters(
                        new DrillDownReportParameters()
                                .withId(EXPENSE_COUNTER)
                                .withDate1(EXPENSE_START_DATE)
                                .withDate2(EXPENSE_END_DATE)))
                .apply(offlineCalls(), setParameters(
                        new DrillDownReportParameters()
                                .withId(COUNTER_OFFLINE_CALLS)
                                .withAccuracy("1")
                                .withDate1(START_DATE_OFFLINE_CALLS)
                                .withDate2(END_DATE_OFFLINE_CALLS)))
                .apply(publishers(), setParameters(
                        new DrillDownReportParameters()
                                .withId(COUNTER_PUBLISHERS)
                                .withAccuracy("1")
                                .withDate1(START_DATE_PUBLISHERS)
                                .withDate2(END_DATE_PUBLISHERS)))
                .apply(vacuum(), setParameters(
                        new DrillDownReportParameters()
                                .withId(YANDEX_EATS_ON_MAPS)
                                .withAccuracy("1")
                                .withDate1(DateConstants.Vacuum.START_DATE)
                                .withDate2(DateConstants.Vacuum.END_DATE)))
                .apply(recommendationWidget(), setParameters(
                        new DrillDownReportParameters()
                                .withId(YANDEX_WEATHER)
                                .withAccuracy("0.001")
                                .withDate1(DateConstants.RecommendationWidget.START_DATE)
                                .withDate2(DateConstants.RecommendationWidget.END_DATE)))
                .apply(cdp(), setParameters(
                        new DrillDownReportParameters()
                                .withId(TEST_CDP)
                                .withAccuracy("1")
                                .withDate1(DateConstants.Cdp.START_DATE)
                                .withDate2(DateConstants.Cdp.END_DATE)))
                .apply(crossDeviceAttribution(), setParameters(
                        new DrillDownReportParameters()
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
                        new TableReportParameters()
                                .withDate1("2016-04-06")
                                .withDate2("2016-04-16")))
                .apply(matches(equalTo("ym:s:usersPurchasePercentage")), setParameters(
                        new TableReportParameters()
                                .withId(ECOMMERCE_TEST)
                                .withDate1(DateConstants.Ecommerce.START_DATE)
                                .withDate2(DateConstants.Ecommerce.END_DATE)))
                .apply(matches(equalTo("ym:s:YMCLIDPercentage")), setParameters(
                        new TableReportParameters()
                                .withId(WIKIMART_RU)
                                .withDate1("2016-06-01")
                                .withDate2("2016-06-14")))
                .apply(matches(equalTo("ym:s:YACLIDPercentage")), setParameters(
                        new TableReportParameters()
                                .withId(YANDEX_MARKET)
                                .withDate1("2016-06-01")
                                .withDate2("2016-06-14")))
                .apply(matches(equalTo("ym:s:goal<goal_id>bounceRate")), setParameters(goalId(53225L)))
                .apply(matches(equalTo("ym:ad:overYearSinceFirstVisitPercentage"))
                        .or(matches(equalTo("ym:ad:upToYearUserRecencyPercentage"))), setParameters(
                        new TableReportParameters()
                                .withDate1("2018-11-01")
                                .withDate2("2018-11-30")))
                .apply(matches((equalTo("ym:s:over54AgePercentage"))), setParameters(
                        new TableReportParameters()
                                .withDate2("2017-05-31")
                                .withDate1("2017-05-20")))
                .apply(matches((equalTo("ym:ad:over54AgePercentage"))), setParameters(
                        new TableReportParameters()
                                .withDate2("2017-05-31")
                                .withDate1("2017-05-01")))
                .apply(parameterized(GOAL_ID).and(matches(anyOf(
                        equalTo("ym:s:goal<goal_id><currency>revenue"),
                        equalTo("ym:s:goal<goal_id>converted<currency>Revenue"),
                        equalTo("ym:ad:goal<goal_id>converted<currency>Revenue"),
                        equalTo("ym:s:conversionRateGroup<goal_id>converted<currency>Revenue"),
                        equalTo("ym:ad:conversionRateGroup<goal_id>converted<currency>Revenue"),
                        equalTo("ym:s:goal<goal_id>revenue")))),
                        setParameters(goalId(SENDFLOWERS_RU)))
                .apply(
                        matches(anyOf(
                                equalTo("ym:s:goal<goal_id><currency>revenue"),
                                equalTo("ym:s:goal<goal_id>converted<currency>Revenue"),
                                equalTo("ym:ad:goal<goal_id>converted<currency>Revenue"),
                                equalTo("ym:s:conversionRateGroup<goal_id>revenue"),
                                equalTo("ym:s:conversionRateGroup<goal_id>converted<currency>Revenue"),
                                equalTo("ym:ad:conversionRateGroup<goal_id>converted<currency>Revenue"),
                                equalTo("ym:s:goal<goal_id>revenue"))),
                        setParameters(
                                new DrillDownReportParameters()
                                        .withDate1(START_DATE)
                                        .withDate2(END_DATE)
                                        .withId(SENDFLOWERS_RU)))
                .build(identity());
    }

    @Before
    public void setup() {
        addTestParameter("Метрика", metricName);
        addTestParameter("Остальное", tail.toString());
    }

    @Test
    @Issue("METR-15726")
    @IgnoreParameters(reason = "no data", tag = "no data")
    @IgnoreParameters(reason = "affinityIndexInterests", tag = "affinity")
    @IgnoreParameters(reason = "METR-23460", tag = "pvl_filter")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkTotalsWithFilterValues() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps().getDrilldownReportAndExpectSuccess(
                tail,
                new CommonReportParameters()
                        .withMetric(metricName)
                        .withFilters(metric(metricName).lessThan(0).build()));

        assumeThat("отчет данных не содержит", result.getData(), empty());

        assertThat("итоговые значения присутствуют", result.getTotals(), everyItem(greaterThan(0d)));
    }

    @Test
    @IgnoreParameters(reason = "no data", tag = "no data")
    @IgnoreParameters(reason = "METR-23460", tag = "pvl_report")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkTotalsInReport() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps().getDrilldownReportAndExpectSuccess(
                tail,
                new CommonReportParameters()
                        .withMetric(metricName));

        List<List<Double>> metrics = user.onResultSteps().getMetrics(result);

        assumeThat("отчет содержит одну строку со значениями метрик", metrics, iterableWithSize(1));

        List<Double> expectedTotals = metrics.get(0);

        assertThat("итоговые значения совпадают со значениями из единственной строки отчета",
                result.getTotals(), equalTo(expectedTotals));
    }

    @Tag(name = "no data")
    public static Collection<Object[]> ignoreNoData() {
        return ImmutableList.<Object[]>builder()
                .add(toArray("ym:ad:productPurchasedUniq", anything()))
                .add(toArray("ym:ad:overYearUserRecencyPercentage", anything()))
                .add(toArray("ym:ad:goal<goal_id>bounceRate", anything()))
                .add(toArray("ym:ad:ecommercePurchases", anything()))
                .add(toArray(both(startsWith("ym:ad:productBasketsRemove")).and(endsWith("Price")), anything()))
                .add(toArray("ym:ad:productBasketsUniq", anything()))
                .add(toArray("ym:ad:GCLIDPercentage", anything()))
                .add(toArray("ym:ad:usersPurchasePercentage", anything()))
                .add(toArray("ym:ad:productPurchasedQuantity", anything()))
                .add(toArray("ym:ad:productBasketsRemoveQuantity", anything()))
                .add(toArray("ym:ad:productImpressions", anything()))
                .add(toArray(both(startsWith("ym:ad:ecommerce")).and(endsWith("Revenue")), anything()))
                .add(toArray("ym:ad:productImpressionsUniq", anything()))
                .add(toArray("ym:ad:YMCLIDPercentage", anything()))
                .add(toArray("ym:ad:sumParams", anything()))
                .add(toArray(both(startsWith("ym:ad:ecommerce")).and(endsWith("RevenuePerPurchase")), anything()))
                .add(toArray("ym:ad:conversionRateGroup<goal_id>revenue", anything()))
                .add(toArray("ym:ad:avgParams", anything()))
                .add(toArray("ym:ad:goal<goal_id>revenue", anything()))
                .add(toArray(both(startsWith("ym:ad:ecommerce")).and(endsWith("RevenuePerVisit")), anything()))
                .add(toArray("ym:ad:conversionRateGroup<goal_id>converted<currency>Revenue", anything()))
                .add(toArray("ym:ad:goal<goal_id>converted<currency>Revenue", anything()))
                .add(toArray("ym:ad:over32VisitsPerUserPercentage", anything()))
                .add(toArray("ym:ad:YACLIDPercentage", anything()))
                .add(toArray("ym:ad:productBasketsQuantity", anything()))
                .add(toArray(both(startsWith("ym:ad:productBaskets")).and(endsWith("Price")), anything()))
                .add(toArray("ym:ad:paramsNumber", anything()))
                .add(toArray(both(startsWith("ym:ad:productPurchased")).and(endsWith("Price")), anything()))
                .add(toArray("ym:ev:overYearUserRecencyPercentage", anything()))
                .build();
    }

    @Tag(name = "affinity")
    public static Collection<Object[]> ignoreAffinity() {
        return ImmutableList.<Object[]>builder()
                .add(toArray("ym:s:affinityIndexInterests", anything()))
                .add(toArray("ym:s:affinityIndexInterests2", anything()))
                .build();
    }

    @IgnoreParameters.Tag(name = "pvl_filter")
    public static Collection<Object[]> ignoreParametersInFilter() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvlAll1Window"), anything()},
                {equalTo("ym:s:pvlAll3Window"), anything()},
                {equalTo("ym:s:pvlAll7Window"), anything()},
                {equalTo("ym:s:pvlAll<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()}
        });
    }

    @IgnoreParameters.Tag(name = "pvl_report")
    public static Collection<Object[]> ignoreParametersInReport() {
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
