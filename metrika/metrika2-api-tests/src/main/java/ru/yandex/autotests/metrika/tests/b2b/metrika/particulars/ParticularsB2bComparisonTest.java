package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.metrika.segments.site.parametrization.Attribution;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_IMAGES;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 20.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.COMPARISON})
@Title("B2B на отобранных вручную параметрах запросов Comparison")
public class ParticularsB2bComparisonTest extends BaseB2bParticularTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createParams("COMPARISON #0",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withFilters_a(dimension("ym:s:trafficSource").equalTo("organic").build())
                                .withFilters_b(dimension("ym:s:trafficSource").equalTo("ad").build())
                                .withDimension("ym:s:datePeriod<group>")
                                .withId(33434543L)
                                .withAccuracy("medium")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru")
                ),
                createParams("COMPARISON #1",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:deviceCategory").equalTo("desktop").build())
                                .withFilters_a(dimension("ym:s:deviceCategory").equalTo("desktop").build())
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters("ym:s:datePeriod<group>!n")
                                .withId(12633481L)
                                .withMetric("ym:s:visits,ym:s:pageviews,ym:s:users,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:datePeriod<group>"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON #2",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:startURLDomain").matchStar("strana-sovetov.com").or(dimension("ym:s:startURLDomain").matchStar("pokushay.ru").or(dimension("ym:s:startURLDomain").matchStar("polismed.ru").or(dimension("ym:s:startURLDomain").matchStar("azbukadiet.ru").or(dimension("ym:s:startURLDomain").matchStar("otvetkak.ru").or(dimension("ym:s:startURLDomain").matchStar("vsezdorovo.com").or(dimension("ym:s:startURLDomain").matchStar("mosadvokat.org").or(dimension("ym:s:startURLDomain").matchStar("house-dacha.ru").or(dimension("ym:s:startURLDomain").matchStar("planshetcomp.ru").or(dimension("ym:s:startURLDomain").matchStar("remrep.ru")))))))))).build())
                                .withFilters_a("(ym:s:startURLDomain=*'strana-sovetov.com' or ym:s:startURLDomain=*'pokushay.ru' or ym:s:startURLDomain=*'polismed.ru' or ym:s:startURLDomain=*'azbukadiet.ru' or ym:s:startURLDomain=*'otvetkak.ru' or ym:s:startURLDomain=*'vsezdorovo.com' or ym:s:startURLDomain=*'mosadvokat.org' or ym:s:startURLDomain=*'house-dacha.ru' or ym:s:startURLDomain=*'planshetcomp.ru' or ym:s:startURLDomain=*'remrep.ru') and (ym:s:visitDuration>60)")
                                .withFilters_a(dimension("ym:s:startURLDomain").matchStar("strana-sovetov.com").or(dimension("ym:s:startURLDomain").matchStar("pokushay.ru").or(dimension("ym:s:startURLDomain").matchStar("polismed.ru").or(dimension("ym:s:startURLDomain").matchStar("azbukadiet.ru").or(dimension("ym:s:startURLDomain").matchStar("otvetkak.ru").or(dimension("ym:s:startURLDomain").matchStar("vsezdorovo.com").or(dimension("ym:s:startURLDomain").matchStar("mosadvokat.org").or(dimension("ym:s:startURLDomain").matchStar("house-dacha.ru").or(dimension("ym:s:startURLDomain").matchStar("planshetcomp.ru").or(dimension("ym:s:startURLDomain").matchStar("remrep.ru")))))))))).and(dimension("ym:s:visitDuration").greaterThan(60)).build())
                                .withSort("-ym:s:visits")
                                .withFilters("ym:s:startURLDomain!n")
                                .withIds(17778574L, 17795725L, 105866L, 22660126L, 18776983L, 25038071L, 21450451L, 11600101L, 1087174L, 17795794L, 13232584L, 23859406L, 17795692L, 17780713L, 18943111L, 17780392L, 20852761L, 20052163L, 16384456L, 23411512L, 25852784L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:startURLDomain"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON #3",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b("")
                                .withFilters_a(dimension("ym:s:trafficSource").equalTo("ad").or(dimension("ym:s:trafficSource").equalTo("organic")).build())
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:endURLPathLevel1Hash").defined().build())
                                .withId(19909813L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:endURLPathLevel1Hash,ym:s:endURLPathLevel2Hash,ym:s:endURLPathLevel3Hash,ym:s:endURLPathLevel4Hash,ym:s:endURLHash"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON #4",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withAccuracy("0.01")
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withMetric("ym:s:users,ym:s:visits,ym:s:visitsPerDay,ym:s:avgVisitDurationSeconds,ym:s:bounceRate,ym:s:pageDepth,ym:s:sumGoalReachesAny,ym:s:anyGoalConversionRate")
                                .withDimension("ym:s:directClickOrder,ym:s:directPlatformType")
                                .withLimit(10000)
                                .withId(101024L)
                ),
                createParams("COMPARISON #6",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b("")
                                .withFilters_a(dimension("ym:s:goal13002544IsReached").equalTo("Yes").or(dimension("ym:s:goal13044434IsReached").equalTo("Yes")).build())
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withId(25306862L)
                                .withMetric("ym:s:visits,ym:s:pageviews,ym:s:users,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:datePeriod<group>"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON #7",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withDimension("ym:s:datePeriod<group>")
                                .withId(21140494L)
                                .withAccuracy("medium")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru")
                ),
                createParams("COMPARISON #8",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2019-06-07")
                                .withDate2_a("2019-06-17")
                                .withDate1_b("2019-06-07")
                                .withDate2_b("2019-06-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withDimension("ym:s:datePeriod<group>")
                                .withId(51384274L)
                                .withAccuracy("medium")
                                .withMetric("ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withLang("ru")
                ),
                createParams("COMPARISON #9",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b("")
                                .withFilters_a("")
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withIds(23346052L, 30736788L, 31415133L, 32022016L, 32007776L, 30714588L, 31354423L, 31415508L, 32021541L, 31689581L, 31856791L, 31856436L, 32021371L, 32007771L, 32007836L, 31769936L, 30694563L, 16443139L, 31856056L, 31313858L)
                                .withMetric("ym:s:visits,ym:s:pageviews,ym:s:users,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:datePeriod<group>")
                ),
                createParams("COMPARISON #10",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:regionCountry").equalTo(225).and(dimension("ym:s:regionArea").equalTo(1)).build())
                                .withFilters_a(dimension("ym:s:regionCountry").equalTo(225).and(dimension("ym:s:regionArea").equalTo(10174)).build())
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withLimit(500)
                                .withId(24376390L)
                                .withMetric("ym:s:visits")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:s:goalDimension")
                ),
                createParams("COMPARISON #11",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:regionCountry").equalTo(225).and(dimension("ym:s:regionArea").equalTo(1)).build())
                                .withFilters_a(dimension("ym:s:browser").in(70).build())
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withId(395386L)
                                .withMetric("ym:s:visits,ym:s:pageviews,ym:s:users,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:datePeriod<group>"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON #12",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(exists(dimension("ym:s:paramsLevel1").equalTo("query").and(dimension("ym:s:paramsLevel2").equalTo("morda"))).and(dimension("ym:s:deviceCategory").equalTo("desktop")).build())
                                .withFilters_a(exists(dimension("ym:s:paramsLevel1").equalTo("query").and(dimension("ym:s:paramsLevel2").equalTo("morda").and(dimension("ym:s:paramsLevel3").equalTo("submit")))).and(dimension("ym:s:deviceCategory").equalTo("tablet")).build())
                                .withSort("-ym:s:datePeriod<group>")
                                .withFilters(dimension("ym:s:datePeriod<group>").defined().build())
                                .withId(YANDEX_IMAGES)
                                .withMetric("ym:s:visits,ym:s:pageviews,ym:s:users,ym:s:percentNewVisitors,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:datePeriod<group>"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON #13",
                        RequestTypes.COMPARISON,
                        new ComparisonReportParameters()
                                .withDate1_a("2021-03-01")
                                .withDate2_a("2021-03-28")
                                .withDate1_b("2021-03-01")
                                .withDate2_b("2021-03-28")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withAccuracy("low")
                                .withFilters_a("(ym:pv:URL=*'https://metrika.yandex.ru/*') and (ym:s:regionCountry IN('149'))")
                                .withFilters_b("(ym:pv:URL=*'https://metrika.yandex.ru/*') and (ym:s:regionCountry IN('149')) and (EXISTS ym:u:userID WITH (ym:u:userVisits>20))")
                                .withSort("norm(ym:s:visits)")
                                .withFilters("ym:s:gender!n")
                                .withId(YANDEX_METRIKA_2_0)
                                .withMetric("norm(ym:s:visits),ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:gender"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                )
        );
    }
}
