package ru.yandex.autotests.metrika.tests.b2b.metrika.usercentric;

import java.util.Collection;
import java.util.Map;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static java.util.Collections.unmodifiableMap;
import static java.util.function.Function.identity;
import static java.util.stream.Collectors.toMap;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.IKEA_VSEM;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.syntaxUserCentric;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.metrika.segments.core.meta.segment.UserFilterType.ATTR;

public class UserCentricFiltersAttrB2bTest extends BaseB2bTest {
    protected static final Counter COUNTER = IKEA_VSEM;
    protected static final String START_DATE = "2017-09-01";
    protected static final String END_DATE = "2017-09-10";

    private static final String FILTER_START_SPECIAL_DATE = "2017-08-31";
    private static final String FILTER_END_SPECIAL_DATE = "2017-09-05";

    private static final Map<String, Expression> FILTERS = unmodifiableMap(Stream.of(
            Pair.of("ym:u:ageInterval", dimension("ym:u:ageInterval").equalTo("25")),
            Pair.of("ym:u:daysSinceFirstVisitOneBased", dimension("ym:u:daysSinceFirstVisitOneBased").equalTo("1")),
            Pair.of("ym:u:firstAdvEngine", dimension("ym:u:firstAdvEngine").equalTo("ya_direct")),
            Pair.of("ym:u:firstReferalSource", dimension("ym:u:firstReferalSource").notDefined()),
            Pair.of("ym:u:firstSearchEngine", dimension("ym:u:firstSearchEngine").equalTo("yandex_search")),
            Pair.of("ym:u:firstSearchEngineRoot", dimension("ym:u:firstSearchEngineRoot").equalTo("yandex")),
            Pair.of("ym:u:firstSearchPhrase", dimension("ym:u:firstSearchPhrase").equalTo("икеа")),
            Pair.of("ym:u:firstSocialNetwork", dimension("ym:u:firstSocialNetwork").notDefined()),
            Pair.of("ym:u:firstSocialNetworkProfile", dimension("ym:u:firstSocialNetworkProfile").notDefined()),
            Pair.of("ym:u:firstTrafficSource", dimension("ym:u:firstTrafficSource").equalTo("ad")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTAdvEngine", dimension("ym:u:CROSS_DEVICE_FIRSTAdvEngine").equalTo("ya_direct")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTReferalSource", dimension("ym:u:CROSS_DEVICE_FIRSTReferalSource").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTSearchEngine", dimension("ym:u:CROSS_DEVICE_FIRSTSearchEngine").equalTo("yandex_search")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTSearchEngineRoot", dimension("ym:u:CROSS_DEVICE_FIRSTSearchEngineRoot").equalTo("yandex")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTSearchPhrase", dimension("ym:u:CROSS_DEVICE_FIRSTSearchPhrase").equalTo("икеа")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTSocialNetwork", dimension("ym:u:CROSS_DEVICE_FIRSTSocialNetwork").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTQRCodeProvider", dimension("ym:u:CROSS_DEVICE_FIRSTQRCodeProvider").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTSocialNetworkProfile", dimension("ym:u:CROSS_DEVICE_FIRSTSocialNetworkProfile").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTTrafficSource", dimension("ym:u:CROSS_DEVICE_FIRSTTrafficSource").equalTo("ad")),

            Pair.of("ym:u:gender", dimension("ym:u:gender").equalTo("male")),
            Pair.of("ym:u:interest", dimension("ym:u:interest").equalTo("literature")),
            Pair.of("ym:u:userFirstVisitDate", dimension("ym:u:userFirstVisitDate").equalTo("2017-09-01")),
            Pair.of("ym:u:lastVisitDate", dimension("ym:u:lastVisitDate").equalTo("2017-09-01")),
            Pair.of("ym:u:firstMessenger", dimension("ym:u:firstMessenger").notEqualTo("skype")),
            Pair.of("ym:u:firstQRCodeProvider", dimension("ym:u:firstQRCodeProvider").notDefined()),
            Pair.of("ym:u:firstRecommendationSystem", dimension("ym:u:firstRecommendationSystem").notEqualTo("pulse")),
            Pair.of("ym:u:firstDirectClickOrder", dimension("ym:u:firstDirectClickOrder").equalTo("11876462")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTMessenger", dimension("ym:u:CROSS_DEVICE_FIRSTMessenger").notEqualTo("skype")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTRecommendationSystem", dimension("ym:u:CROSS_DEVICE_FIRSTRecommendationSystem").notEqualTo("pulse")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectClickOrder", dimension("ym:u:CROSS_DEVICE_FIRSTDirectClickOrder").equalTo("11876462")),

            Pair.of("ym:u:firstDirectBannerGroup", dimension("ym:u:firstDirectBannerGroup").equalTo("1472194565")),
            Pair.of("ym:u:firstDirectPlatformType", dimension("ym:u:firstDirectPlatformType").equalTo("search")),
            Pair.of("ym:u:firstDirectPlatform", dimension("ym:u:firstDirectPlatform").equalTo("0.yandex.ru")),
            Pair.of("ym:u:firstDirectSearchPhrase", dimension("ym:u:firstDirectSearchPhrase").equalTo("www ikea ru")),
            Pair.of("ym:u:firstDirectClickBanner", dimension("ym:u:firstDirectClickBanner").equalTo("1.3116437299")),
            Pair.of("ym:u:firstDirectBannerText", dimension("ym:u:firstDirectBannerText").equalTo("Доставка товаров ИКЕА в квартиру, без предоплаты! ИКЕА. Заказывайте у нас!")),
            Pair.of("ym:u:firstDirectConditionType", dimension("ym:u:firstDirectConditionType").equalTo("phrase")),
            Pair.of("ym:u:firstDirectPhraseOrCond", dimension("ym:u:firstDirectPhraseOrCond").equalTo("\"ИКЕА\"")),
            Pair.of("ym:u:firstDirectOfferComplexID", dimension("ym:u:firstDirectOfferComplexID").notDefined()),
            Pair.of("ym:u:firstDisplayCampaign", dimension("ym:u:firstDisplayCampaign").notDefined()),
            Pair.of("ym:u:firstFrom", dimension("ym:u:firstFrom").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectBannerGroup", dimension("ym:u:CROSS_DEVICE_FIRSTDirectBannerGroup").equalTo("1472194565")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectPlatformType", dimension("ym:u:CROSS_DEVICE_FIRSTDirectPlatformType").equalTo("search")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectPlatform", dimension("ym:u:CROSS_DEVICE_FIRSTDirectPlatform").equalTo("0.yandex.ru")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectSearchPhrase", dimension("ym:u:CROSS_DEVICE_FIRSTDirectSearchPhrase").equalTo("www ikea ru")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectClickBanner", dimension("ym:u:CROSS_DEVICE_FIRSTDirectClickBanner").equalTo("1.3116437299")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectBannerText", dimension("ym:u:CROSS_DEVICE_FIRSTDirectBannerText").equalTo("Доставка товаров ИКЕА в квартиру, без предоплаты! ИКЕА. Заказывайте у нас!")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectConditionType", dimension("ym:u:CROSS_DEVICE_FIRSTDirectConditionType").equalTo("phrase")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectPhraseOrCond", dimension("ym:u:CROSS_DEVICE_FIRSTDirectPhraseOrCond").equalTo("\"ИКЕА\"")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDirectOfferComplexID", dimension("ym:u:CROSS_DEVICE_FIRSTDirectOfferComplexID").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTDisplayCampaign", dimension("ym:u:CROSS_DEVICE_FIRSTDisplayCampaign").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTFrom", dimension("ym:u:CROSS_DEVICE_FIRSTFrom").notDefined()),

            Pair.of("ym:u:firstUTMSource", dimension("ym:u:firstUTMSource").equalTo("google")),
            Pair.of("ym:u:firstUTMMedium", dimension("ym:u:firstUTMMedium").equalTo("cpc")),
            Pair.of("ym:u:firstUTMCampaign", dimension("ym:u:firstUTMCampaign").equalTo("820097752")),
            Pair.of("ym:u:firstUTMContent", dimension("ym:u:firstUTMContent").equalTo("194470388858")),
            Pair.of("ym:u:firstUTMTerm", dimension("ym:u:firstUTMTerm").equalTo("икеа каталог")),
            Pair.of("ym:u:firstOpenstatService", dimension("ym:u:firstOpenstatService").notDefined()),
            Pair.of("ym:u:firstOpenstatCampaign", dimension("ym:u:firstOpenstatCampaign").notDefined()),
            Pair.of("ym:u:firstOpenstatAd", dimension("ym:u:firstOpenstatAd").notDefined()),
            Pair.of("ym:u:firstOpenstatSource", dimension("ym:u:firstOpenstatSource").notDefined()),
            Pair.of("ym:u:firstHasGCLID", dimension("ym:u:firstHasGCLID").equalTo("Yes")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTUTMSource", dimension("ym:u:CROSS_DEVICE_FIRSTUTMSource").equalTo("google")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTUTMMedium", dimension("ym:u:CROSS_DEVICE_FIRSTUTMMedium").equalTo("cpc")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTUTMCampaign", dimension("ym:u:CROSS_DEVICE_FIRSTUTMCampaign").equalTo("820097752")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTUTMContent", dimension("ym:u:CROSS_DEVICE_FIRSTUTMContent").equalTo("194470388858")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTUTMTerm", dimension("ym:u:CROSS_DEVICE_FIRSTUTMTerm").equalTo("икеа каталог")),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTOpenstatService", dimension("ym:u:CROSS_DEVICE_FIRSTOpenstatService").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTOpenstatCampaign", dimension("ym:u:CROSS_DEVICE_FIRSTOpenstatCampaign").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTOpenstatAd", dimension("ym:u:CROSS_DEVICE_FIRSTOpenstatAd").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTOpenstatSource", dimension("ym:u:CROSS_DEVICE_FIRSTOpenstatSource").notDefined()),
            Pair.of("ym:u:CROSS_DEVICE_FIRSTHasGCLID", dimension("ym:u:CROSS_DEVICE_FIRSTHasGCLID").equalTo("Yes")),

            // параметры которые нужно заигнорить
            Pair.of("ym:s:isRobot", dimension("ym:s:isRobot").notDefined()),
            Pair.of("ym:u:interest2d1", dimension("ym:u:interest2d1").notDefined()),
            Pair.of("ym:up:paramsLevel1", dimension("ym:up:paramsLevel1").notDefined()),
            Pair.of("ym:u:clientID", dimension("ym:u:clientID").notDefined())
    ).collect(toMap(Pair::getKey, Pair::getValue)));

    public IFormParameters dateFilterParameters;

    @Parameterized.Parameter()
    public Expression filter;

    @Parameterized.Parameter(1)
    public String metricName;

    @Parameterized.Parameter(2)
    public UserCentricParamsHolder userCentricParamsHolder;

    @Parameterized.Parameters(name = "фильтр {0} метрика {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(userOnTest.onUserCentricMetadataSteps().getFilters(ATTR, FILTERS, FILTER_START_SPECIAL_DATE, FILTER_END_SPECIAL_DATE))
                .vectorValues(MultiplicationBuilder.<String, String, UserCentricParamsHolder>builder(
                        userOnTest.onMetadataSteps().getMetrics(syntaxUserCentric()), UserCentricParamsHolder::new)
                        .apply(any(),
                                (d, h) -> {
                                    h.setCounter(COUNTER);
                                    h.setDate1(START_DATE);
                                    h.setDate2(END_DATE);
                                    return Stream.of(Pair.of(d, h));
                                })
                        .apply(table(TableEnum.VISITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(userOnTest.onMetadataSteps()
                                                            .getDimensions(syntaxUserCentric().and(table(TableEnum.VISITS)))));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.HITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(userOnTest.onMetadataSteps()
                                                            .getDimensions(syntaxUserCentric().and(table(TableEnum.HITS)))));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.ADVERTISING),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withDimension(userOnTest.onMetadataSteps()
                                                            .getDimensions(syntaxUserCentric().and(table(TableEnum.ADVERTISING))))
                                                    .withDirectClientLogins(
                                                            userOnTest.onManagementSteps().onClientSteps().getClientLogins(
                                                                    new ClientsParameters()
                                                                            .withCounters(COUNTER.get(ID))
                                                                            .withDate1(START_DATE)
                                                                            .withDate2(END_DATE),
                                                                    ulogin(COUNTER.get(U_LOGIN)))),
                                            currency("643"));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(identity()))
                .build();
    }

    @Override
    public void check() {
        Object referenceBean = userOnRef.onReportSteps().getRawReport(
                requestType,
                dateFilterParameters,
                reportParameters,
                userCentricParamsHolder.getTail());
        Object testingBean = userOnTest.onReportSteps().getRawReport(
                requestType,
                dateFilterParameters,
                reportParameters,
                userCentricParamsHolder.getTail());

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, beanEquivalent(referenceBean).fields(getIgnore()).withVariation(doubleWithAccuracy));
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }

    protected IFormParameters getReportParameters() {
        return new CommonReportParameters()
                .withId(userCentricParamsHolder.getCounter().get(ID))
                .withMetric(metricName);
    }

    @IgnoreParameters.Tag(name = "no data")
    public static Collection<Object[]> ignoreParametersNoData() {
        return asList(new Object[][]{
                // для этих аттрибутов нет данных
                {having(on(Expression.class).build(), containsString("ym:s:isRobot")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:interest2d1")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:up:paramsLevel1")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:clientID")), anything(), anything()}
        });
    }
}
