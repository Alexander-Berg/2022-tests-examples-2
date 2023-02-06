package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.singlerowfilter;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParametersList;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.startsWith;
import static org.hamcrest.core.Every.everyItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.commons.rules.IgnoreParameters.Tag;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DRESSTOP;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.NOTIK;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_UPLOADINGS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_EATS_ON_MAPS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_MARKET;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_WEATHER;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.ATTRIBUTION;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.ADVERTISING;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.HITS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters.experimentId;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.matchers.IgnoreTrailingSlashMatcher.equalToIgnoringTrailingSlash;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.interest2;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.interest2Name;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.offlineCalls;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.publishers;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.recommendationWidget;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.url;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.vacuum;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.utils.Utils.flatten;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.LAST;


/**
 * Created by konkov on 19.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Отчет 'таблица': фильтр по значению измерения")
@RunWith(Parameterized.class)
public class SingleRowByDimension {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = YANDEX_MARKET;

    private static final String START_DATE = "2017-02-20";
    private static final String END_DATE = "2017-02-20";

    private static final Counter ADVERTISING_COUNTER = DRESSTOP;
    private static final String ADVERTISING_START_DATE = DateConstants.Advertising.START_DATE;
    private static final String ADVERTISING_END_DATE = DateConstants.Advertising.END_DATE;

    private static final String ADVERTISING_METRIC = "ym:ad:clicks";
    private static final String HIT_METRIC = "ym:pv:pageviews";
    private static final String VISIT_METRIC = "ym:s:visits";

    private static final String HITS_START_DATE = "2015-03-19";
    private static final String HITS_END_DATE = "2015-03-19";

    private static final String DIRECT_SEARCH_PHRASE = "ym:s:lastDirectSearchPhrase";
    private static final String MARKET_SEARCH_PHRASE = "ym:s:marketSearchPhrase";
    private static final String START_DATE_FOR_SEARCH_PHRASE = "2017-02-16";
    private static final String END_DATE_FOR_SEARCH_PHRASE = "2017-02-16";

    private static final String FIRST_OPENSTAT_SOURCE = "ym:s:firstOpenstatSource";
    private static final String START_DATE_FOR_OPENSTAT_SOURCE = "2017-02-28";
    private static final String END_DATE_FOR_OPENSTAT_SOURCE = "2017-02-28";

    private static final Counter COUNTER_ECOMMERCE = ECOMMERCE_TEST;
    private static final String START_DATE_ECOMMERCE = DateConstants.Ecommerce.START_DATE;
    private static final String END_DATE_ECOMMERCE = DateConstants.Ecommerce.END_DATE;

    public static final Counter COUNTER_YAN = Counters.YANDEX_NEWS;
    private static final String START_DATE_YAN = DateConstants.Yan.START_DATE;
    private static final String END_DATE_YAN = DateConstants.Yan.END_DATE;

    private static final String DISPLAY_CAMPAIGN = "ym:s:lastDisplayCampaign";
    private static final String DISPLAY_CAMPAIGN_START_DATE = "2015-08-26";
    private static final String DISPLAY_CAMPAIGN_END_DATE = "2015-08-26";
    private static final Counter DISPLAY_CAMPAIGN_COUNTER = NOTIK;

    private static final Counter COUNTER_OFFLINE_CALLS = TEST_UPLOADINGS;
    private static final String START_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.START_DATE;
    private static final String END_DATE_OFFLINE_CALLS = DateConstants.OfflineCalls.END_DATE;

    private static final Counter COUNTER_PUBLISHERS = Counters.EUROPA_PLUS;
    private static final String START_DATE_PUBLISHERS = DateConstants.Publishers.START_DATE;
    private static final String END_DATE_PUBLISHERS = DateConstants.Publishers.END_DATE;

    private static final List<String> SOURCES_9_10_DIMENSIONS = Arrays.asList(
            "ym:s:<attribution>Messenger",
            "ym:s:<attribution>RecommendationSystem",
            "ym:s:firstMessenger",
            "ym:s:firstRecommendationSystem",
            "ym:s:lastSignMessenger",
            "ym:s:lastSignRecommendationSystem",
            "ym:s:messenger",
            "ym:s:recommendationSystem"
    );

    private static final String TRAFIC_SOURCE_START_DATE = "2019-04-20";
    private static final String TRAFIC_SOURCE_END_DATE = "2019-04-20";
    private static final Counter TRAFIC_SOURCE_COUNTER = SENDFLOWERS_RU;

    private static final List<String> QR_CODE_PROVIDER_ATTRIBUTES = Arrays.asList(
            "ym:s:<attribution>QRCodeProvider",
            "ym:s:<attribution>QRCodeProviderName",
            "ym:s:QRCodeProvider",
            "ym:s:QRCodeProviderName",
            "ym:s:firstQRCodeProvider",
            "ym:s:firstQRCodeProviderName",
            "ym:s:lastSignQRCodeProvider",
            "ym:s:lastSignQRCodeProviderName"
    );

    public static final Counter QR_CODE_PROVIDER_COUNTER = YANDEX_METRIKA_2_0;
    public static final String QR_CODE_PROVIDER_START_DATE = "2022-01-17";
    public static final String QR_CODE_PROVIDER_END_DATE = "2022-01-31";


    private static final String INTEREST2_DATE = "2018-08-24";
    private static final String EXPERIMENT_DATE = "2016-03-01";

    private static Collection<String> urlDimensions;

    private String dimensionValue;
    private String filter;

    @Parameter()
    public String dimensionName;

    @Parameter(1)
    public FreeFormParameters tail;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                user.onMetadataSteps().getDimensions(
                        table(HITS).or(table(VISITS)).or(table(ADVERTISING)).and(interest2Name().negate())
                ),
                FreeFormParameters::makeParameters)
                //параметры, общие для всех измерений
                .apply(any(), setParameters((String dimensionName) ->
                        new TableReportParameters()
                                .withId(COUNTER.get(ID))
                                .withDimension(dimensionName)
                                .withAccuracy("1")
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)))
                //подставим атрибуцию
                .apply(parameterized(ATTRIBUTION), setParameters(
                        new ParametrizationParameters().withAttribution(LAST)))
                .apply(parameterized(ParametrizationTypeEnum.EXPERIMENT), setParameters(aggregate(
                        new TableReportParameters()
                                .withId(KVAZI_KAZINO)
                                .withDate1(EXPERIMENT_DATE)
                                .withDate2(EXPERIMENT_DATE),
                        experimentId(KVAZI_KAZINO))))
                //для ecommerce свои даты и счетчик
                .apply(ecommerce(), setParameters(
                        new TableReportParameters()
                                .withId(COUNTER_ECOMMERCE)
                                .withDate1(START_DATE_ECOMMERCE)
                                .withDate2(END_DATE_ECOMMERCE)))
                .apply(interest2(), setParameters(
                        new TableReportParameters()
                                .withDate1(INTEREST2_DATE)
                                .withDate2(INTEREST2_DATE)))
                .apply(yan(), setParameters(
                        new TableReportParameters()
                                .withId(COUNTER_YAN)
                                .withDate1(START_DATE_YAN)
                                .withDate2(END_DATE_YAN)
                                .withAccuracy("0.1")))
                .apply(table(HITS), setParameters(
                        new TableReportParameters()
                                .withMetric(HIT_METRIC)
                                .withDate1(HITS_START_DATE)
                                .withDate2(HITS_END_DATE)
                                .withSort(sort().by(HIT_METRIC).descending().build())))
                .apply(table(VISITS), setParameters(
                        new TableReportParameters()
                                .withMetric(VISIT_METRIC)
                                .withSort(sort().by(VISIT_METRIC).descending().build())))
                .apply(table(ADVERTISING), setParameters(
                        new TableReportParameters()
                                .withMetric(ADVERTISING_METRIC)
                                .withSort(sort().by(ADVERTISING_METRIC).descending().build())
                                .withId(ADVERTISING_COUNTER)
                                .withAccuracy("0.01")
                                .withDate1(ADVERTISING_START_DATE)
                                .withDate2(ADVERTISING_END_DATE)
                                .withDirectClientLogins(
                                        user.onManagementSteps().onClientSteps().getClientLogins(
                                                new ClientsParameters()
                                                        .withCounters(ADVERTISING_COUNTER.get(ID))
                                                        .withDate1(ADVERTISING_START_DATE)
                                                        .withDate2(ADVERTISING_END_DATE),
                                                ulogin(ADVERTISING_COUNTER.get(U_LOGIN))))))
                .apply(matches(equalTo(DISPLAY_CAMPAIGN)), setParameters(
                        new TableReportParameters()
                                .withId(DISPLAY_CAMPAIGN_COUNTER.get(ID))
                                .withDate1(DISPLAY_CAMPAIGN_START_DATE)
                                .withDate2(DISPLAY_CAMPAIGN_END_DATE)))
                .apply(matches(equalTo(DIRECT_SEARCH_PHRASE)).or(matches(equalTo(MARKET_SEARCH_PHRASE))), setParameters(
                        new TableReportParameters()
                                .withDate1(START_DATE_FOR_SEARCH_PHRASE)
                                .withDate2(END_DATE_FOR_SEARCH_PHRASE)))
                .apply(matches(equalTo(FIRST_OPENSTAT_SOURCE)), setParameters(
                        new TableReportParameters()
                                .withDate1(START_DATE_FOR_OPENSTAT_SOURCE)
                                .withDate2(END_DATE_FOR_OPENSTAT_SOURCE)))
                .apply(matches(equalTo("ym:s:networkType")), setParameters(
                        new TableReportParameters()
                                .withDate1("2017-01-20")
                                .withDate2("2017-01-21")))
                .apply(matches(containsString("DirectBanner"))
                        .or(matches(containsString("directBanner")))
                        .or(matches(containsString("DirectPhraseOrCond"))), setParameters(
                        new TableReportParameters()
                                .withAccuracy("0.001")
                                .withDate1("2016-03-01")
                                .withDate2("2016-03-01")))
                .apply(offlineCalls(), setParameters(
                        new TableReportParameters()
                                .withId(COUNTER_OFFLINE_CALLS)
                                .withAccuracy("1")
                                .withDate1(START_DATE_OFFLINE_CALLS)
                                .withDate2(END_DATE_OFFLINE_CALLS)))
                .apply(publishers(), setParameters(
                        new TableReportParameters()
                                .withId(COUNTER_PUBLISHERS)
                                .withAccuracy("1")
                                .withDate1(START_DATE_PUBLISHERS)
                                .withDate2(END_DATE_PUBLISHERS)))
                .apply(vacuum(), setParameters(
                        new TableReportParameters()
                                .withId(YANDEX_EATS_ON_MAPS)
                                .withAccuracy("1")
                                .withDate1(DateConstants.Vacuum.START_DATE)
                                .withDate2(DateConstants.Vacuum.END_DATE)))
                .apply(recommendationWidget(), setParameters(
                        new TableReportParameters()
                                .withId(YANDEX_WEATHER)
                                .withAccuracy("0.001")
                                .withDate1(DateConstants.RecommendationWidget.START_DATE)
                                .withDate2(DateConstants.RecommendationWidget.END_DATE)))
                .apply(SOURCES_9_10_DIMENSIONS::contains, setParameters(
                        new TableReportParameters()
                                .withId(TRAFIC_SOURCE_COUNTER)
                                .withAccuracy("1")
                                .withDate1(TRAFIC_SOURCE_START_DATE)
                                .withDate2(TRAFIC_SOURCE_END_DATE)))
                .apply(QR_CODE_PROVIDER_ATTRIBUTES::contains, setParameters(
                        new TableReportParameters()
                                .withId(QR_CODE_PROVIDER_COUNTER)
                                .withAccuracy("1")
                                .withDate1(QR_CODE_PROVIDER_START_DATE)
                                .withDate2(QR_CODE_PROVIDER_END_DATE)))
                .build(identity());
    }

    @BeforeClass
    public static void init() {
        urlDimensions = user.onMetadataSteps().getDimensionsRaw(url());
    }

    @Before
    public void setup() {
        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withLimit(1),
                tail);

        assumeThat("запрос вернул ровно одну строку", result.getData(), iterableWithSize(1));

        addTestParameter("Измерение", dimensionName);

        dimensionValue = user.onResultSteps().getDimensions(result).get(0).get(0);

        filter = dimension(dimensionName).equalTo(dimensionValue).build();

        addTestParameter("Фильтр", filter);
    }

    @Test
    @IgnoreParametersList({
            @IgnoreParameters(reason = "Данные для теста не существуют", tag = "no data"),
            @IgnoreParameters(reason = "METR-25245", tag = "*Name"),
            @IgnoreParameters(reason = "Новые данные - пока не появились в базе", tag = "METR-26881"),
            @IgnoreParameters(reason = "Новые данные - пока не появились в базе", tag = "recommendations urls"),
            @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    })
    public void singleRowTest() {
        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withFilters(filter),
                tail);

        //для проверки корректности значений измерений извлекаем их в линейный список
        List<String> dimensions = flatten(user.onResultSteps().getDimensions(result));

        assertThat("значение измерения в каждой строке равно заданному", dimensions,
                both(Matchers.<String>iterableWithSize(greaterThan(0)))
                        .and(everyItem(getDimensionValueMatcher(dimensionName, dimensionValue))));
    }

    private static Matcher<String> getDimensionValueMatcher(String dimensionName, String dimensionValue) {
        return urlDimensions.contains(dimensionName)
                ? equalToIgnoringTrailingSlash(dimensionValue)
                : equalTo(dimensionValue);
    }

    @Tag(name = "no data")
    public static Collection ignoredParametersNoData() {
        return asList(new Object[][]{
                {"ym:ad:displayCampaign", anything()},
                {"ym:ad:firstDisplayCampaign", anything()},
                {"ym:ad:lastDisplayCampaign", anything()},
                {"ym:ad:lastSignDisplayCampaign", anything()},
                {"ym:ad:<attribution>DisplayCampaign", anything()},

                {"ym:pv:hasAdBlocker", anything()},
                {"ym:pv:hasAdBlockerName", anything()},
                {"ym:pv:YMCLID", anything()},
                {"ym:pv:YACLID", anything()},

                {"ym:s:PProductBrand", anything()},

                {"ym:s:YACLID", anything()},

                {"ym:s:offlinePointLocationID", anything()},
                {"ym:s:offlinePointRegionID", anything()}
        });
    }

    @Tag(name = "*Name")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {endsWith("Name"), anything()}
        });
    }

    @Tag(name = "METR-26881")
    public static Collection<Object[]> ignoreParametersMetr26881() {
        return asList(new Object[][]{
                {endsWith("turboPageID"), anything()}
        });
    }

    @Tag(name = "recommendations urls")
    public static Collection<Object[]> ignoreParametersRecommendationsUrls() {
        return asList(new Object[][]{
                {startsWith("ym:pv:recommendationURL"), anything()}
        });
    }

    @IgnoreParameters.Tag(name = "adfox")
    public static Collection<Object[]> ignoreParametersAdfox() {
        return asList(new Object[][]{
                {containsString("adfox"), anything()}
        });
    }
}
