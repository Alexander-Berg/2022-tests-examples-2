package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.metrika.segments.site.parametrization.Attribution;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

/**
 * Created by sourx on 20.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.DRILLDOWN})
@Title("B2B на отобранных вручную параметрах запросов Drilldown")
public class ParticularsB2bDrilldownTest extends BaseB2bParticularTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                createParams("METR-16650 Неправильный фильтр для параметров визитов для drilldown",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withAccuracy("0.01")
                                .withId(YANDEX_IMAGES.get(ID))
                                .withDimensions(of("ym:s:paramsLevel1", "ym:s:paramsLevel2"))
                                .withParentIds(singletonList("query"))
                                .withMetrics(of(
                                        "ym:s:visits",
                                        "ym:s:sumParams",
                                        "ym:s:avgParams",
                                        "ym:s:paramsNumber",
                                        "ym:s:bounceRate",
                                        "ym:s:pageDepth",
                                        "ym:s:avgVisitDurationSeconds"))
                                .withSort(sort().by("ym:s:visits").descending().build())
                                .withDate1("2015-06-01")
                                .withDate2("2015-06-10")),
                createParams("METRIKASUPP-7388 Ошибка 4004 при добавлении цели в Директ-расходах",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-09-08")
                                .withDate2("2016-10-07")
                                .withDimension(of(
                                        "ym:ad:<attribution>DirectOrder",
                                        "ym:ad:<attribution>DirectBannerGroup"
                                ))
                                .withMetric("ym:ad:goal<goal_id><currency>AdCost")
                                .withDirectClientIds(SENDFLOWERS_RU.get(Counter.CLIENT_IDS))
                                .withAccuracy("0.01"),
                        goalId(5133668L),
                        currency("643")),
                createParams("DRILLDOWN #0",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:trafficSource").equalTo("organic").build())
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withId(33302385L)
                                .withAccuracy("0.1")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("DRILLDOWN #1",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:UTMSource").defined().build())
                                .withLimit(50)
                                .withId(32138655L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:s:UTMSource,ym:s:UTMMedium,ym:s:UTMCampaign,ym:s:UTMContent,ym:s:UTMTerm"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("DRILLDOWN #2",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:startURL").matchStar("*2015/09*").or(dimension("ym:s:startURL").matchStar("*2015/10*")).and(dimension("ym:s:bounce").equalTo("No")).and(dimension("ym:s:startURLPathLevel1Hash").defined()).build())
                                .withLimit(50)
                                .withId(24247498L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:s:startURLPathLevel1Hash,ym:s:startURLPathLevel2Hash,ym:s:startURLPathLevel3Hash,ym:s:startURLPathLevel4Hash,ym:s:startURLHash")
                ),
                createParams("DRILLDOWN #3",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:regionCountry").defined().build())
                                .withDimension("ym:s:regionCountry,ym:s:regionArea,ym:s:regionCity")
                                .withId(16973272L)
                                .withAccuracy("0.1")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru")
                ),
                createParams("DRILLDOWN #4",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:trafficSource").equalTo("organic").or(dimension("ym:s:trafficSource").equalTo("direct").or(dimension("ym:s:trafficSource").equalTo("social"))).build())
                                .withLimit(50)
                                .withId(22227335L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                ),
                createParams("DRILLDOWN #5",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:ad:goal<goal_id>conversionRate")
                                .withFilters(dimension("ym:ad:<attribution>DirectOrder").defined().build())
                                .withDirectClientLogins(asList("spetsyug.artinnweb"))
                                .withDimension("ym:ad:<attribution>DirectOrder,ym:ad:<attribution>DirectBanner,ym:ad:<attribution>DirectPhraseOrCond,ym:ad:<attribution>DirectSearchPhrase")
                                .withId(14416603L)
                                .withAccuracy("0.01")
                                .withMetric("ym:ad:goal<goal_id>conversionRate,ym:ad:goal<goal_id>reaches,ym:ad:goal<goal_id>visits,ym:ad:goal<goal_id>users,ym:ad:goal<goal_id><currency>CPA,ym:ad:goal<goal_id>clicks,ym:ad:goal<goal_id><currency>AdCost,ym:ad:goal<goal_id>bounceRate,ym:ad:goal<goal_id>pageDepth,ym:ad:goal<goal_id>avgVisitDurationSeconds")
                                .withLang("ru"),
                        goalId(39527287L),
                        currency("643"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("DRILLDOWN #6",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:goal<goal_id>conversionRate")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withId(6519262L)
                                .withAccuracy("0.1")
                                .withMetric("ym:s:goal<goal_id>conversionRate,ym:s:goal<goal_id>reaches,ym:s:goal<goal_id>visits,ym:s:goal<goal_id>users,ym:s:goal<goal_id>bounceRate,ym:s:goal<goal_id>pageDepth,ym:s:goal<goal_id>avgVisitDurationSeconds")
                                .withLang("ru"),
                        goalId(13898640L),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("DRILLDOWN #7",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:dl:downloads")
                                .withFilters(dimension("ym:dl:URLPathLevel1Hash").defined().build())
                                .withDimension("ym:dl:URLPathLevel1Hash,ym:dl:URLPathLevel2Hash,ym:dl:URLPathLevel3Hash,ym:dl:URLPathLevel4Hash,ym:dl:URLHash")
                                .withId(29481630L)
                                .withAccuracy("0.1")
                                .withMetric("ym:dl:downloads,ym:dl:users")
                                .withLang("ru")
                ),
                createParams("DRILLDOWN #8",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:visits")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withId(101024L)
                                .withAccuracy("0.1")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("DRILLDOWN #9",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:deviceCategory").defined().build())
                                .withDimension("ym:s:deviceCategory,ym:s:mobilePhone,ym:s:mobilePhoneModel")
                                .withId(31781751L)
                                .withAccuracy("0.1")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru")
                ),
                createParams("DRILLDOWN #10",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:regionCountry").equalTo(225).and(dimension("ym:s:regionArea").equalTo(1)).and(dimension("ym:s:searchEngineRoot").notEqualTo("yandex").or(dimension("ym:s:searchEngine").notEqualTo("yandex_maps"))).and(dimension("ym:s:lastSignUTMSource").notMatchStar("yandex_%7Bsource%7D")).and(dimension("ym:s:marketSearchPhrase").notMatchStar("%D0%BC%D0%B8%D0%BC%D0%B8")).or(dimension("ym:s:marketSearchPhrase").notMatchStar("mimi").or(dimension("ym:s:marketSearchPhrase").notMatchStar("mi-mi").or(dimension("ym:s:marketSearchPhrase").notMatchStar("%D0%BC%D0%B8-%D0%BC%D0%B8").or(dimension("ym:s:marketSearchPhrase").notMatchStar("%D1%8C%D1%88%D1%8C%D1%88%D1%8B%D1%8C%D1%84%D0%BA%D0%B5").or(dimension("ym:s:marketSearchPhrase").notMatchStar("%D0%BC%D0%B8%D0%BC%D0%B8%D1%81%D0%BC%D0%B0%D1%80%D1%82").or(dimension("ym:s:marketSearchPhrase").notMatchStar("mimismart").or(dimension("ym:s:marketSearchPhrase").notMatchStar("mimi-smart").and(dimension("ym:s:trafficSource").equalTo("organic"))))))))).build())
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withId(36215605L)
                                .withAccuracy("0.1")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru")
                ),
                createParams("DRILLDOWN #11",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1("2020-02-29")
                                .withDate2("2020-03-06")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:vacuumevents")
                                .withDimension("ym:s:vacuumSurface,ym:s:vacuumEvent,ym:s:<attribution>TrafficSource,ym:s:vacuumOrganization")
                                .withId(57358270L)
                                .withAccuracy("1")
                                .withMetric("ym:s:vacuumevents")
                                .withConfidence(true)
                                .withLang("ru")
                                .withParentIds(asList("websearch", "show_org"))
                ),
                createParams("METRIKASUPP-12892 using parentId for join attributes with ownAdditionals",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withDate1(DateConstants.Expense.START_DATE)
                                .withDate2(DateConstants.Expense.END_DATE)
                                .withAccuracy("0.1")
                                .withId(TEST_EXPENSES.get(ID))
                                .withMetric("ym:ev:visits")
                                .withDimension("ym:ev:<attribution>ExpenseSource,ym:ev:<attribution>ExpenseMedium,ym:ev:<attribution>ExpenseCampaign")
                                .withSort("-ym:ev:visits")
                                .withParentIds(singletonList("1.google")),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LASTSIGN)
                ),
                createParams("METRIKASUPP-12694 drilldown secrecy",
                        RequestTypes.DRILLDOWN,
                        new DrillDownReportParameters()
                                .withId(NOTIK)
                                .withDate1("2020-02-01")
                                .withDate2("2020-02-01")
                                .withDimension("ym:s:startURLHash,ym:s:deviceCategory,ym:s:lastSignSourceEngine")
                                .withMetric("ym:s:visits")
                                .withSort("-ym:s:visits")
                                .withParentIds(singletonList("17005692970411835408"))
                                .withAccuracy("1")
                )
        );
    }
}
