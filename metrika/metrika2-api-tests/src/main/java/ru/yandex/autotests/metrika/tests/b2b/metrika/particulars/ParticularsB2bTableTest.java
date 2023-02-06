package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import com.google.common.collect.ImmutableList;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.metrika.segments.site.parametrization.Attribution;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.GOAL_ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Relation.none;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by sourx on 20.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.TABLE})
@Title("B2B на отобранных вручную параметрах запросов Table")
public class ParticularsB2bTableTest extends BaseB2bParticularTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                createParams("METR-17993 фильтр по url parameters",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU.get(ID))
                                .withDimension("ym:s:goal")
                                .withMetric("ym:s:users")
                                .withFilters(none(dimension("ym:pv:URLParamName").equalTo("category")).build())
                                .withDate1("2015-09-07")
                                .withDate2("2015-09-13")),
                createParams("METR-18004 Не сходятся данные в итого и в таблице",
                        RequestTypes.ECOMMERCE_ORDERS_TABLE,
                        new TableReportParameters()
                                .withId(SHATURA_COM.get(ID))
                                .withDimensions(of("ym:s:PPurchaseID", "ym:s:PProduct"))
                                .withMetrics(of("ym:s:pProductPurchasedQuantity", "ym:s:pProductPurchasedRevenue"))
                                .withFilters(dimension("ym:s:PProductName")
                                        .matchSubstring("G86-01.T8М, Ящик подкроватный для 2сп.кроватей (AA7, ABC)")
                                        .build())
                                .withDate1("2015-09-21")
                                .withDate2("2015-09-24")),
                createParams("METR-17813 сегментация не работает https://st.yandex-team.ru/METR-17813#1441274673000",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(NOTIK.get(ID))
                                .withMetric("ym:s:visits")
                                .withFilters(dimension("ym:s:advEngine").equalTo("display").build())
                                .withDate1("2015-09-20")
                                .withDate2("2015-09-21")),
                createParams("METR-18306 503-я ошибка в ответе сервера API",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(MIR_NEDVIZHIMOSTY.get(ID))
                                .withDimensions(of(
                                        "ym:s:dateTime",
                                        "ym:s:browser",
                                        "ym:s:operatingSystem",
                                        "ym:s:regionCity",
                                        "ym:s:screenWidth",
                                        "ym:s:screenHeight",
                                        "ym:s:firstSourceEngine",
                                        "ym:s:firstSearchPhrase",
                                        "ym:s:deviceCategory",
                                        "ym:s:trafficSource"))
                                .withMetrics(ImmutableList.of(
                                        "ym:s:pageviews",
                                        "ym:s:goal2329921reaches",
                                        "ym:s:goal2329924reaches",
                                        "ym:s:goal2329927reaches",
                                        "ym:s:goal2329930reaches",
                                        "ym:s:goal4831613reaches",
                                        "ym:s:goal5041133reaches",
                                        "ym:s:goal5041139reaches",
                                        "ym:s:goal5247422reaches",
                                        "ym:s:goal5247425reaches",
                                        "ym:s:goal5247428reaches",
                                        "ym:s:goal11794826reaches",
                                        "ym:s:goal18245755reaches"))
                                .withDate1("2015-10-05")
                                .withDate2("2015-10-05")
                                .withLimit(9999)),
                createParams("TESTIRT-7367 отчет по группе счетчиков",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withIds(of(DEMOCRAT_SPB, Counters.DOCTORHEAD))
                                .withMetric("ym:s:visits")
                                .withDate1("2015-09-01")
                                .withDate2("2015-09-01")),
                createParams("METR-18215 Падает фильтр ym:s:regionCountry=.(149,10000)",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withMetric("ym:s:visits")
                                .withDate1("2015-09-24")
                                .withAccuracy("1")
                                .withFilters(dimension("ym:s:regionCountry").in("149", "10000").build())),
                createParams("METRIKASUPP-6805 При сегментации по просмотру URL условие \"или\" не работает",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(PRODUCT)
                                .withMetrics(of("ym:s:visits",
                                        "ym:s:pageDepth",
                                        "ym:s:avgVisitDurationSeconds"))
                                .withDimensions(of("ym:s:browser",
                                        "ym:s:browserAndVersionMajor",
                                        "ym:s:browserAndVersion"))
                                .withDate1("2016-04-13")
                                .withDate2("2016-04-19")
                                .withAccuracy("1")
                                .withFilters(dimension("ym:pv:URL").matchSubstring("/products/35432/")
                                        .or(dimension("ym:pv:URL").matchSubstring("/products/35436/")).build())),
                createParams("METR-17832 странное параметрах визитов (1)",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(TEST_ECOMMERCE)
                                .withDate1("2015-10-07")
                                .withDate2("2015-10-07")
                                .withDimension("ym:s:paramsLevel1")
                                .withMetrics(of("ym:s:visits[ym:s:paramsLevel2=='a2']",
                                        "ym:s:visits[ym:s:paramsLevel2=='b2']",
                                        "ym:s:visits[ym:s:paramsLevel2=='c2']",
                                        "ym:s:visits[ym:s:paramsLevel3=='a3']",
                                        "ym:s:visits[ym:s:paramsLevel3=='b3']",
                                        "ym:s:visits[ym:s:paramsLevel3=='c3']"))
                                .withSort("ym:s:paramsLevel1")
                                .withAccuracy("1")),
                createParams("METR-17832 странное параметрах визитов (2)",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(TEST_ECOMMERCE)
                                .withDate1("2015-10-07")
                                .withDate2("2015-10-07")
                                .withDimension("ym:s:paramsLevel1")
                                .withMetric("ym:s:visits[ym:s:paramsLevel2!='a2' AND ym:s:paramsLevel2!='b2']")
                                .withSort("ym:s:paramsLevel1")
                                .withAccuracy("1")),
                createParams("METR-22246 Значение конверсии отличается от прода в отчете Конверсия",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withMetrics(of("ym:s:goalDimensionInternalReaches",
                                        "ym:s:sumVisits"))
                                .withDimension("ym:s:goalDimension")
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-04-20")
                                .withDate2("2016-05-19")
                                .withAccuracy("1")
                                .withIncludeUndefined(true)),
                createParams("METR-22862 NumberFormatException: For input string при задании цели в отчетах ecommerce",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withAccuracy("0.1")
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:productName")
                                .withFilters("ym:s:productBrand!n")
                                .withMetrics(of(
                                        "ym:s:goal<goal_id>conversionRate",
                                        "ym:s:goal<goal_id>reaches",
                                        "ym:s:goal<goal_id>visits",
                                        "ym:s:goal<goal_id>productBasketsQuantity",
                                        "ym:s:goal<goal_id>productBasketsUniq",
                                        "ym:s:goal<goal_id>productBasketsPrice",
                                        "ym:s:goal<goal_id>productPurchasedQuantity")),
                        goalId(5133671L)),
                createParams("METRIKASUPP-8441 direct platform filter",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2017-06-25")
                                .withDate2("2017-08-07")
                                .withDimension("ym:u:firstDirectPlatform")
                                .withFilters(dimension("ym:u:firstDirectPlatform").equalTo("2.go.mail.ru").build())
                                .withMetric("ym:u:users")),
                createParams("TABLE #0",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().and(metric("ym:s:goal<goal_id>reaches").greaterThan(0)).build())
                                .withLimit(50)
                                .withId(27719604L)
                                .withMetric("ym:s:goal<goal_id>conversionRate,ym:s:goal<goal_id>reaches,ym:s:goal<goal_id>visits,ym:s:goal<goal_id>pageviews,ym:s:goal<goal_id>users,ym:s:goal<goal_id>percentNewVisitors,ym:s:goal<goal_id>bounceRate,ym:s:goal<goal_id>pageDepth,ym:s:goal<goal_id>avgVisitDurationSeconds")
                                .withLang("ru")
                                .withDimension("ym:s:datePeriod<group>"),
                        goalId(7062144L),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("TABLE #1",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withId(33606344L)
                                .withDimension("ym:s:startURL")
                                .withMetric("ym:s:users")
                                .withFilters("ym:s:<attribution>SearchEngineRoot=='yandex'")
                                .withLimit(1)
                                .withAccuracy("1")
                ),
                createParams("TABLE #2",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(1)
                                .withIncludeUndefined(true)
                                .withFilters(dimension("ym:s:pageViews").greaterThan(3).and(exists(dimension("ym:u:userVisits").greaterThan(2)).and(dimension("ym:s:datePeriod<group>").defined())).build())
                                .withDimension("ym:s:datePeriod<group>")
                                .withId(20679409L)
                                .withAccuracy("0.1")
                                .withMetric("ym:s:visits")
                                .withLang("ru")
                ),
                createParams("TABLE #3",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withSort("-ym:pv:pageviews")
                                .withFilters(dimension("ym:pv:URL").matchSubstring("auto.ru/cars/bmw/used").or(dimension("ym:pv:regionAreaName").matchSubstring("auto.ru/cars/bmw/used")).or(dimension("ym:pv:regionCityName").matchSubstring("auto.ru/cars/bmw/used")).and(dimension("ym:pv:URLHash").defined()).build())
                                .withLimit(100)
                                .withId(22753222L)
                                .withMetric("ym:pv:pageviews")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:pv:URLHash,ym:pv:regionArea,ym:pv:regionCity")
                ),
                createParams("METR-28504 Duplicate column in USING list",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withDate1("2018-03-01")
                                .withDate2("2018-03-31")
                                .withMetrics(new String[]{"ym:ad:visits",
                                        "ym:ad:users",
                                        "ym:ad:clicks",
                                        "ym:ad:<currency>AdCost",
                                        "ym:ad:bounceRate",
                                        "ym:ad:pageDepth",
                                        "ym:ad:avgVisitDurationSeconds",
                                        "ym:ad:anyGoalConversionRate",
                                        "ym:ad:sumGoalReachesAny"})
                                .withDimensions(new String[] {"ym:ad:lastDirectPlatform",
                                        "ym:ad:firstDirectPlatform",
                                        "ym:ad:lastSignDirectPlatform",
                                        "ym:ad:<attribution>DirectPlatform"})
                                .withFilters("(ym:ad:lastSignDirectPlatformType=='context')")
                                .withSort("ym:ad:users")
                                .withDirectClientLogins("pirania74.ru")
                                .withIds(501087L),
                        new CurrencyParameters().currency("643"),
                        new ParametrizationParameters().withAttribution(Attribution.LAST)
                ),
                createParams("METR-40694 ym:pv:pageviews with filter EXISTS (ym:s:goal and ym:s:specialDefaultDate)",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withMetric("ym:pv:pageviews")
                                .withFilters("EXISTS (ym:s:goal == " + SENDFLOWERS_RU.get(GOAL_ID) + " and ym:s:specialDefaultDate<'5daysAgo')")
                                .withId(SENDFLOWERS_RU.get(ID))
                )
        );
    }
}
