package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.metrika.segments.site.parametrization.Attribution;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 20.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.COMPARISON_DRILLDOWN})
@Title("B2B на отобранных вручную параметрах запросов ComparisonDrilldown")
public class ParticularsB2bComparisonDrilldownTest extends BaseB2bParticularTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                createParams("COMPARISON_DRILLDOWN #0",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withId(30636312L)
                                .withDimension("ym:s:startURL")
                                .withMetric("ym:s:users")
                                .withFilters(dimension("ym:s:<attribution>SearchEngineRoot").equalTo("yandex").build())
                                .withLimit(1L)
                                .withAccuracy("full")
                ),
                createParams("COMPARISON_DRILLDOWN #1",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withOffset(1L)
                                .withLimit(10)
                                .withIncludeUndefined(false)
                                .withSort("-ym:sp:sumHitsForAllHits")
                                .withDimension("ym:sp:URLHash")
                                .withId(20871571L)
                                .withMetric("ym:sp:sumHitsForAllHits")
                                .withLang("ru")
                ),
                createParams("COMPARISON_DRILLDOWN #2",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:pv:URL").matchStar("*basket*").and(dimension("ym:s:firstTrafficSource").equalTo("organic")).build())
                                .withFilters_a(dimension("ym:pv:URL").matchStar("*basket*").and(dimension("ym:s:firstTrafficSource").equalTo("ad")).build())
                                .withSort("-ym:s:visits")
                                .withId(22828843L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds,ym:s:users")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.FIRST)
                ),
                createParams("COMPARISON_DRILLDOWN #3",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withIncludeUndefined(false)
                                .withDimension("ym:s:<attribution>TrafficSource")
                                .withId(31472133L)
                                .withMetric("ym:s:visits")
                                .withLang("ru")
                ),
                createParams("COMPARISON_DRILLDOWN #4",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:searchPhrase").notMatchStar("*���*").and(dimension("ym:s:searchPhrase").notMatchStar("*newform*").and(dimension("ym:s:searchPhrase").notMatchStar("*new*").and(dimension("ym:s:searchPhrase").notMatchStar("*newform*").and(dimension("ym:s:searchPhrase").notMatchStar("*�������*"))))).build())
                                .withFilters_a(dimension("ym:s:searchPhrase").notMatchStar("*���*").and(dimension("ym:s:searchPhrase").notMatchStar("*newform*").and(dimension("ym:s:searchPhrase").notMatchStar("*new*").and(dimension("ym:s:searchPhrase").notMatchStar("*newform*").and(dimension("ym:s:searchPhrase").notMatchStar("*�������*").and(dimension("ym:s:searchPhrase").notMatchStar("*new form*").and(dimension("ym:s:searchPhrase").notMatchStar("newform*").and(dimension("ym:s:searchPhrase").notMatchStar("*��� ����*")))))))).build())
                                .withSort("-ym:s:visits")
                                .withId(5293174L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds,ym:s:users")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine,ym:s:firstSearchPhrase"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON_DRILLDOWN #5",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:pv:URL").matchStar("*basket*").and(dimension("ym:s:firstTrafficSource").equalTo("organic")).build())
                                .withFilters_a(dimension("ym:pv:URL").matchStar("*basket*").and(dimension("ym:s:firstTrafficSource").equalTo("ad")).build())
                                .withSort("-ym:s:visits")
                                .withId(22828843L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds,ym:s:users")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.FIRST)
                ),
                createParams("COMPARISON_DRILLDOWN #6",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:deviceCategory").equalTo("mobile").and(dimension("ym:s:physicalScreenWidth").equalTo(1080).and(dimension("ym:s:physicalScreenHeight").equalTo(1920))).build())
                                .withFilters_a(dimension("ym:s:deviceCategory").equalTo("mobile").and(dimension("ym:s:physicalScreenWidth").equalTo(720).and(dimension("ym:s:physicalScreenHeight").equalTo(1280))).build())
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:deviceCategory").defined().build())
                                .withId(20690443L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")

                                .withDimension("ym:s:deviceCategory,ym:s:mobilePhone,ym:s:mobilePhoneModel"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON_DRILLDOWN #7",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:physicalScreenWidth").equalTo(720).and(dimension("ym:s:deviceCategory").equalTo("mobile")).build())
                                .withFilters_a(dimension("ym:s:physicalScreenWidth").equalTo(720).and(dimension("ym:s:deviceCategory").equalTo("mobile")).build())
                                .withSort("-ym:s:visits")
                                .withFilters(dimension("ym:s:deviceCategory").defined().build())
                                .withId(20690443L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:deviceCategory,ym:s:mobilePhone,ym:s:mobilePhoneModel"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON_DRILLDOWN #8",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withId(33606344L)
                                .withDimension("ym:s:startURL")
                                .withMetric("ym:s:users")
                                .withFilters(dimension("ym:s:<attribution>SearchEngineRoot").equalTo("yandex").build())
                                .withLimit(1L)
                                .withAccuracy("full")
                ),
                createParams("COMPARISON_DRILLDOWN #9",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:regionCountry").equalTo(149).and(dimension("ym:s:deviceCategory").equalTo("desktop")).build())
                                .withFilters_a(dimension("ym:s:regionCountry").equalTo(149).and(dimension("ym:s:deviceCategory").equalTo("desktop")).build())
                                .withSort("-ym:pv:pageviews")
                                .withFilters(dimension("ym:pv:URLPathLevel1Hash").defined().build())
                                .withId(722545L)
                                .withMetric("ym:pv:pageviews,ym:pv:users")
                                .withDimension("ym:pv:URLPathLevel1Hash,ym:pv:URLPathLevel2Hash,ym:pv:URLPathLevel3Hash"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON_DRILLDOWN #10",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50L)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b("")
                                .withFilters_a(dimension("ym:pv:URL").matchStar("http://mosigra.ru/allgames/skidki/").build())
                                .withSort("-ym:s:visits")
                                .withId(183746L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON_DRILLDOWN #11",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withId(37921650L)
                                .withDimension("ym:s:startURL")
                                .withMetric("ym:s:users")
                                .withFilters(dimension("ym:s:<attribution>SearchEngineRoot").equalTo("google").build())
                                .withLimit(1L)
                                .withAccuracy("full")
                ),
                createParams("COMPARISON_DRILLDOWN #12",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withLimit(50)
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withOffset(1L)
                                .withFilters_b(dimension("ym:s:ageInterval").equalTo(25).or(dimension("ym:s:ageInterval").equalTo(45).or(dimension("ym:s:ageInterval").equalTo(35).or(dimension("ym:s:ageInterval").equalTo(18)))).and(dimension("ym:s:gender").equalTo("male")).build())
                                .withFilters_a(dimension("ym:s:ageInterval").equalTo(25).or(dimension("ym:s:ageInterval").equalTo(45).or(dimension("ym:s:ageInterval").equalTo(35).or(dimension("ym:s:ageInterval").equalTo(18)))).and(dimension("ym:s:gender").equalTo("male")).build())
                                .withSort("-ym:s:visits")
                                .withFilters("ym:s:UTMSource!n")
                                .withId(29831514L)
                                .withMetric("ym:s:visits,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:UTMSource,ym:s:UTMMedium,ym:s:UTMCampaign,ym:s:UTMContent,ym:s:UTMTerm"),
                        new ParametrizationParameters()
                                .withAttribution(Attribution.LAST)
                ),
                createParams("COMPARISON_DRILLDOWN #13",
                        RequestTypes.COMPARISON_DRILLDOWN,
                        new ComparisonDrilldownReportParameters()
                                .withDate1_a("2017-02-07")
                                .withDate2_a("2017-02-17")
                                .withDate1_b("2017-02-07")
                                .withDate2_b("2017-02-17")
                                .withOffset(1L)
                                .withLimit(1)
                                .withIncludeUndefined(true)
                                .withFilters(dimension("ym:s:pageViews").greaterThan(3).and(dimension("ym:u:userVisits").greaterThan(2)).and(dimension("ym:s:datePeriod<group>").defined()).build())
                                .withDimension("ym:s:datePeriod<group>")
                                .withId(20679409L)
                                .withAccuracy("medium")
                                .withMetric("ym:s:visits")
                                .withLang("ru")
                )
        );
    }
}

