package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import java.util.Arrays;
import java.util.Collection;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bExpenseTest;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.GENVIC_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.LAMODA_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.STRANALED;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_EXPENSES;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.THERESPO_COM;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.WIKIMART_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_MAPS;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 20.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.BYTIME})
@Title("B2B на отобранных вручную параметрах запросов Bytime")
public class ParticularsB2bBytimeTest extends BaseB2bParticularTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(createParams("METR-18015 Странные провалы в запросе к API",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(YANDEX_MAPS.get(ID))
                                .withMetric("ym:s:users")
                                .withFilters(dimension("ym:s:regionCountry").equalTo(225).build())
                                .withGroup(GroupEnum.DAY)
                                .withDate1("2014-09-21")
                                .withDate2("2015-09-10")
                ))
                .add(createParams(
                        "METR-17625 Для группы можно выбрать группировку по целям https://st.yandex-team" +
                                ".ru/METR-17625#1439572510000",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(WIKIMART_RU.get(ID))
                                .withRowIds(asList(asList(new String[]{null})))
                                .withDimension("ym:s:gender")
                                .withMetric("ym:s:visits")
                                .withDate1("2015-09-01")
                                .withDate2("2015-09-10")
                                .withGroup(GroupEnum.DAY)
                ))
                .add(createParams("METR-18771 Lamoda: pазные данные на графике и в таблице",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(LAMODA_RU)
                                .withMetric("ym:s:visits")
                                .withFilters(
                                        dimension("ym:pv:referer").matchStar("*default-women*is_sale=1*")
                                                .and(dimension("ym:pv:URL").matchStar("*lamoda.ru/p/*"))
                                                .and(dimension("ym:s:datePeriodday").defined()).build())
                                .withDate1("2015-11-10")
                                .withDate2("2015-11-10")
                                .withGroup(GroupEnum.DAY)
                ))
                .add(createParams("METR-18554 Сервис временно недоступен, если не указан параметр chart_type в урле",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(GENVIC_RU)
                                .withRowIds(of(of("2216301")))
                                .withDimensions(of(
                                        "ym:ad:directOrder",
                                        "ym:ad:directBanner",
                                        "ym:ad:directPhraseOrCond",
                                        "ym:ad:directSearchPhrase"))
                                .withMetric("ym:ad:visits")
                                .withFilters(dimension("ym:ad:directOrder").equalTo("2216301").build())
                                .withDate1("2015-10-23")
                                .withDate2("2015-10-29")
                                .withDirectClientLogins(singletonList(GENVIC_RU.get(Counter.U_LOGIN)))
                ))
                .add(createParams("METR-18978 goalDimensionInternalReaches считает визиты вместо достижений цели в totals",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(THERESPO_COM)
                                .withRowIds(asList(of(12366718), of(12368133), of(12368138), of(12368143),
                                        of(13012624), of(13015039), of(13015044), of(13015049), of(13049624),
                                        of(13426955), of(13835032), of(13835037), of(13835042), of(13835187),
                                        of(13835337)))
                                .withDimension("ym:s:goalDimension")
                                .withMetrics(of("ym:s:goalDimensionInternalReaches", "ym:s:sumVisits"))
                                .withDate1("2015-10-30")
                                .withDate2("2015-11-09")
                                .withGroup(GroupEnum.DAY)
                ))
                .add(createParams("METRIKASUPP-6585 Не срабатывает сегментация \"исключить\" в отчете",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(STRANALED)
                                .withMetric("ym:pv:pageviews")
                                .withDimensions(of("ym:pv:URLPathLevel1Hash",
                                        "ym:pv:URLPathLevel2Hash",
                                        "ym:pv:URLPathLevel3Hash",
                                        "ym:pv:URLPathLevel4Hash",
                                        "ym:pv:URLHash"))
                                .withDate1("2016-02-01")
                                .withDate2("2016-02-29")
                                .withGroup(GroupEnum.DAY)
                                .withAccuracy("1")
                                .withFilters(dimension("ym:s:regionCountry").notEqualTo("225")
                                        .or(dimension("ym:s:regionArea").notEqualTo("11162"))
                                        .and(dimension("ym:s:regionCountry").notEqualTo("225")
                                                .or(dimension("ym:s:regionArea").notEqualTo("11282"))).build())
                ))
                .add(createParams("METR-22544 Не работает IN с вложенными tuple",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withAccuracy("0.01")
                                .withDate1("2016-08-06")
                                .withDate2("2016-09-05")
                                .withDimensions(of("ym:s:browser",
                                        "ym:s:browserAndVersionMajor",
                                        "ym:s:browserAndVersion"))
                                .withMetric("ym:s:visits")
                                .withRowIds(of(asList(6, 6.52, "6.52.0"), asList(83, 83.52, "83.52.0")))
                ))
                .add(createParams("METR-25568 фильтр по x=*'_' and x=='_' превращается в противоречие",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withAccuracy("0.01")
                                .withDate1("2017-06-17")
                                .withDate2("2017-06-23")
                                .withRowIds(of(of("save_card")))
                                .withDimension("ym:pv:URLParamName")
                                .withMetrics(of("ym:pv:pageviews"))
                                .withFilters(dimension("ym:pv:URLParamName").matchStar("save_card").build())
                                .withGroup(GroupEnum.DAY)
                ))
                .add(createParams("BY_TIME #0",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withGroup("dekaminute")
                                .withId(41741394L)
                                .withLang("ru")
                                .withMetric("ym:s:bounceRate"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("BY_TIME #1",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withRowIds(of(asList("direct"), asList("organic"), asList("social")))
                                .withIncludeUndefined(false)
                                .withGroup("dekaminute")
                                .withDimension("ym:s:<attribution>TrafficSource")
                                .withId(28232601L)
                                .withMetric("ym:s:newUsers")
                                .withLang("ru")
                ))
                .add(createParams("BY_TIME #2",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withFilters(dimension("ym:s:startURL").matchStar("http://dvaproraba.ru/catalog/okna-dveri-furnitura/laminirovannie-dveri/*").or(dimension("ym:s:startURL").matchStar("http://dvaproraba.ru/catalog/okna-dveri-furnitura/shponirovannie-dveri/")).build())
                                .withLimit(50)
                                .withRowIds(asList(of("organic"), of("direct"), of("internal")))
                                .withId(1225230L)
                                .withMetric("ym:s:visits")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withGroup("day"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("BY_TIME #3",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(10000)
                                .withRowIds(asList(of(12366718), of(12368133), of(12368138), of(12368143), of(13012624), of(13015039), of(13015044), of(13015049), of(13049624), of(13426955), of(13835032), of(13835037), of(13835042), of(13835187), of(13835337)))
                                .withId(31256393L)
                                .withMetric("ym:s:goalDimensionInternalReaches,ym:s:sumVisits")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:s:goalDimension")
                                .withGroup("day")
                ))
                .add(createParams("BY_TIME #4",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withRowIds(of(asList("ad")))
                                .withIncludeUndefined(true)
                                .withGroup("dekaminute")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withId(97404L)
                                .withAccuracy("medium")
                                .withMetric("ym:s:users")
                                .withLang("ru"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("BY_TIME #5",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withFilters(dimension("ym:s:startURL").matchStar("http://allmallorca.ru/beaches/'").and(dimension("ym:s:startURLHash").defined()).build())
                                .withLimit(50)
                                .withRowIds(of(asList("2197730038457837840", "direct", null, null), asList("2197730038457837840", "organic", "organic.yandex", "����� �������"), asList("2197730038457837840", "organic", "organic.yandex", "������ ����� �������"), asList("2197730038457837840", "organic", "organic.yandex", "������� ����"), asList("2197730038457837840", "internal", "internal.allmallorca.ru", null)))
                                .withId(28386431L)
                                .withMetric("ym:s:visits")
                                .withIncludeUndefined(true)
                                .withLang("ru")
                                .withDimension("ym:s:startURLHash,ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine,ym:s:<attribution>SearchPhrase")
                                .withGroup("day"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("BY_TIME #6",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withId(40234229L)
                                .withMetric("ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withGroup("dekaminute")
                                .withRowIds(of(asList("direct"), asList("ad")))
                                .withSort("-ym:s:visits")
                                .withLang("ru"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("BY_TIME #9",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withRowIds(of(of("ad"), of("referral"), of("internal")))
                                .withIncludeUndefined(true)
                                .withGroup("dekaminute")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                                .withId(40552420L)
                                .withAccuracy("medium")
                                .withMetric("ym:s:visits")
                                .withLang("ru"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("BY_TIME #10",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withId(38230L)
                                .withMetric("ym:s:visits")
                                .withDimension("ym:s:<attribution>TrafficSource")
                                .withGroup("dekaminute")
                                .withRowIds(of(asList("ad"), asList("direct"), asList("internal")))
                                .withLang("ru"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("BY_TIME #12",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2017-02-07")
                                .withDate2("2017-02-17")
                                .withOffset(1L)
                                .withLimit(50)
                                .withRowIds(of(of("organic")))
                                .withIncludeUndefined(true)
                                .withGroup("dekaminute")
                                .withDimension("ym:s:<attribution>TrafficSource,ym:s:regionArea,ym:s:<attribution>SourceEngine,ym:s:startURLPathLevel2Hash")
                                .withId(21297280L)
                                .withAccuracy("medium")
                                .withMetric("ym:s:visits")
                                .withLang("ru"),
                        new ParametrizationParameters()
                                .withAttribution("Last")
                ))
                .add(createParams("METRIQA-3277 добавлен тест в Переходы из социальных сетей → Не определено",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("2013-04-01")
                                .withDate2("2013-04-30")
                                .withRowIds(of(of("social.null")))
                                .withDimension("ym:s:LastSourceEngine")
                                .withId(101024L)
                                .withMetric("ym:s:visits")
                                .withLang("ru")
                ))
                .add(createParams("METR-32093 тест для источников паблишеров",
                        RequestTypes.BY_TIME,
                        new BytimeReportParameters()
                                .withDate1("4daysAgo")
                                .withDate2("1daysAgo")
                                .withDimension("ym:s:publisherTrafficSource2")
                                .withId(45543195L)
                                .withMetric("ym:s:publisherviews,ym:s:users")
                                .withSort("-ym:s:publisherviews")
                                .withFilters("ym:s:publisherArticle!n")
                                .withGroup(GroupEnum.DAY)
                                .withLang("ru")
                ))
                .addAll(Stream.of(GroupEnum.ALL, GroupEnum.YEAR, GroupEnum.QUARTER, GroupEnum.MONTH, GroupEnum.WEEK, GroupEnum.DAY)
                        .map(group -> createParams("METR-38506 группировка по времени в отчете по ROI, group=" + group,
                                RequestTypes.BY_TIME,
                                makeParameters()
                                        .append(ulogin(TEST_EXPENSES.get(Counter.U_LOGIN)))
                                        .append(new CommonReportParameters()
                                                .withId(TEST_EXPENSES.get(Counter.ID))
                                                .withDirectClientLogins(userOnTest.onManagementSteps().onClientSteps().getClientLogins(
                                                        new ClientsParameters().withCounters(TEST_EXPENSES.get(Counter.ID)),
                                                        ulogin(TEST_EXPENSES.get(Counter.U_LOGIN))
                                                ))
                                        )
                                        .append(BaseB2bExpenseTest.dateParameters())
                                        .append(new BytimeReportParameters()
                                                .withDate1(DateConstants.Expense.START_DATE)
                                                .withDate2(DateConstants.Expense.END_DATE)
                                                .withDimension("ym:ev:<attribution>ExpenseSource")
                                                .withMetric("ym:ev:expenses<currency>")
                                                .withGroup(group)
                                        )
                        ))
                        .collect(Collectors.toList())
                )
                .build();
    }
}
