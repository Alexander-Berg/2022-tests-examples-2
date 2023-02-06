package ru.yandex.autotests.metrika.tests.b2b.metrika.usercentric;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Stream;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static com.google.common.collect.ImmutableList.of;
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
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.metrika.segments.core.meta.segment.UserFilterType.EVENT;

public class UserCentricFiltersEventB2bTest extends BaseB2bTest {
    protected static final Counter COUNTER = IKEA_VSEM;
    protected static final String START_DATE = "2017-09-01";
    protected static final String END_DATE = "2017-09-10";

    private static final String FILTER_START_SPECIAL_DATE = "2017-08-31";
    private static final String FILTER_END_SPECIAL_DATE = "2017-09-05";

    private static final Map<String, Expression> FILTERS = unmodifiableMap(Stream.of(
            Pair.of("ym:dl:downloadURL", dimension("ym:dl:downloadURL").defined()),
            Pair.of("ym:el:externalLink", dimension("ym:el:externalLink").defined()),
            Pair.of("ym:pv:URL", dimension("ym:pv:URL").equalTo("http://ikea-vsem.ru/")),
            Pair.of("ym:s:advEngine", dimension("ym:s:advEngine").equalTo("ya_direct")),
            Pair.of("ym:s:browser", dimension("ym:s:browser").equalTo("70")),
            Pair.of("ym:s:browserAndVersionMajor", dimension("ym:s:browserAndVersionMajor").equalTo("70.15")),
            Pair.of("ym:s:browserCountry", dimension("ym:s:browserCountry").equalTo("ru")),
            Pair.of("ym:s:browserEngine", dimension("ym:s:browserEngine").equalTo("WebKit")),
            Pair.of("ym:s:browserEngineVersion1", dimension("ym:s:browserEngineVersion1").equalTo("600")),
            Pair.of("ym:s:browserLanguage", dimension("ym:s:browserLanguage").equalTo("ru")),

            Pair.of("ym:s:clientTimeZone", dimension("ym:s:clientTimeZone").equalTo("GMT+04:00")),
            Pair.of("ym:s:cookieEnabled", dimension("ym:s:cookieEnabled").equalTo("yes")),
            Pair.of("ym:s:date", dimension("ym:s:date").equalTo("2017-09-02")),
            Pair.of("ym:s:deviceCategory", dimension("ym:s:deviceCategory").equalTo("mobile")),
            Pair.of("ym:s:directBannerGroup", dimension("ym:s:directBannerGroup").equalTo("2087407183")),
            Pair.of("ym:s:directBannerText", dimension("ym:s:directBannerText").matchStar("*ИКЕА*")),
            Pair.of("ym:s:directClickOrder", dimension("ym:s:directClickOrder").defined()),
            Pair.of("ym:s:directCondition", dimension("ym:s:directCondition").defined()),
            Pair.of("ym:s:directConditionType", dimension("ym:s:directConditionType").equalTo("phrase")),
            Pair.of("ym:s:directPlatform", dimension("ym:s:directPlatform").equalTo("0.yandex.ru")),

            Pair.of("ym:s:directPlatformType", dimension("ym:s:directPlatformType").equalTo("search")),
            Pair.of("ym:s:directSearchPhrase", dimension("ym:s:directSearchPhrase").equalTo("икеа каталог")),
            Pair.of("ym:s:directPhraseOrCond", dimension("ym:s:directPhraseOrCond").equalTo("1.146129061")),
            Pair.of("ym:s:flashEnabled", dimension("ym:s:flashEnabled").equalTo("no")),
            Pair.of("ym:s:hasGCLID", dimension("ym:s:hasGCLID").equalTo("no")),
            Pair.of("ym:s:impressionProductCategoryLevel2", dimension("ym:s:impressionProductCategoryLevel2").notDefined()),
            Pair.of("ym:s:impressionProductCategoryLevel3", dimension("ym:s:impressionProductCategoryLevel3").notDefined()),
            Pair.of("ym:s:impressionProductCategoryLevel4", dimension("ym:s:impressionProductCategoryLevel4").notDefined()),
            Pair.of("ym:s:impressionProductCategoryLevel5", dimension("ym:s:impressionProductCategoryLevel5").notDefined()),

            Pair.of("ym:s:javascriptEnabled", dimension("ym:s:javascriptEnabled").equalTo("yes")),
            Pair.of("ym:s:mobilePhone", dimension("ym:s:mobilePhone").equalTo("1")),
            Pair.of("ym:s:mobilePhoneModel", dimension("ym:s:mobilePhoneModel").equalTo("iPhone")),
            Pair.of("ym:s:openstatAd", dimension("ym:s:openstatAd").notDefined()),
            Pair.of("ym:s:openstatCampaign", dimension("ym:s:openstatCampaign").notDefined()),
            Pair.of("ym:s:openstatService", dimension("ym:s:openstatService").notDefined()),
            Pair.of("ym:s:openstatSource", dimension("ym:s:openstatSource").notDefined()),
            Pair.of("ym:s:operatingSystem", dimension("ym:s:operatingSystem").equalTo("33")),
            Pair.of("ym:s:operatingSystemRoot", dimension("ym:s:operatingSystemRoot").equalTo("108")),
            Pair.of("ym:s:paramsLevel10", dimension("ym:s:paramsLevel10").notDefined()),

            Pair.of("ym:s:paramsLevel2", dimension("ym:s:paramsLevel2").notDefined()),
            Pair.of("ym:s:paramsLevel3", dimension("ym:s:paramsLevel3").notDefined()),
            Pair.of("ym:s:paramsLevel4", dimension("ym:s:paramsLevel4").notDefined()),
            Pair.of("ym:s:paramsLevel5", dimension("ym:s:paramsLevel5").notDefined()),
            Pair.of("ym:s:paramsLevel6", dimension("ym:s:paramsLevel6").notDefined()),
            Pair.of("ym:s:paramsLevel7", dimension("ym:s:paramsLevel7").notDefined()),
            Pair.of("ym:s:paramsLevel8", dimension("ym:s:paramsLevel8").notDefined()),
            Pair.of("ym:s:paramsLevel9", dimension("ym:s:paramsLevel9").notDefined()),
            Pair.of("ym:s:purchaseID", dimension("ym:s:purchaseID").notDefined()),

            Pair.of("ym:s:purchaseProductCategoryLevel2", dimension("ym:s:purchaseProductCategoryLevel2").notDefined()),
            Pair.of("ym:s:purchaseProductCategoryLevel3", dimension("ym:s:purchaseProductCategoryLevel3").notDefined()),
            Pair.of("ym:s:purchaseProductCategoryLevel4", dimension("ym:s:purchaseProductCategoryLevel4").notDefined()),
            Pair.of("ym:s:purchaseProductCategoryLevel5", dimension("ym:s:purchaseProductCategoryLevel5").notDefined()),
            Pair.of("ym:s:referalSource", dimension("ym:s:referalSource").notDefined()),
            Pair.of("ym:s:regionArea", dimension("ym:s:regionArea").equalTo("1")),
            Pair.of("ym:s:regionCity", dimension("ym:s:regionCity").equalTo("213")),
            Pair.of("ym:s:regionCitySize", dimension("ym:s:regionCitySize").equalTo("2m")),
            Pair.of("ym:s:regionCountry", dimension("ym:s:regionCountry").equalTo("225")),

            Pair.of("ym:s:searchEngine", dimension("ym:s:searchEngine").equalTo("yandex_search")),
            Pair.of("ym:s:searchEngineRoot", dimension("ym:s:searchEngineRoot").equalTo("yandex")),
            Pair.of("ym:s:searchPhrase", dimension("ym:s:searchPhrase").equalTo("икеа каталог")),
            Pair.of("ym:s:socialNetwork", dimension("ym:s:socialNetwork").notDefined()),
            Pair.of("ym:s:socialNetworkProfile", dimension("ym:s:socialNetworkProfile").notDefined()),
            Pair.of("ym:s:startURL", dimension("ym:s:startURL").equalTo("http://ikea-vsem.ru/")),
            Pair.of("ym:s:trafficSource", dimension("ym:s:trafficSource").equalTo("direct")),
            Pair.of("ym:s:messenger", dimension("ym:s:messenger").notEqualTo("skype")),
            Pair.of("ym:s:QRCodeProvider", dimension("ym:s:QRCodeProvider").notDefined()),
            Pair.of("ym:s:recommendationSystem", dimension("ym:s:recommendationSystem").notEqualTo("pulse")),
            Pair.of("ym:s:hasAdBlocker", dimension("ym:s:hasAdBlocker").equalTo("no")),
            Pair.of("ym:s:silverlightEnabled", dimension("ym:s:silverlightEnabled").equalTo("no")),
            Pair.of("ym:s:screenFormat", dimension("ym:s:screenFormat").equalTo("16:9")),
            Pair.of("ym:s:screenColors", dimension("ym:s:screenColors").equalTo("24")),
            Pair.of("ym:s:screenWidth", dimension("ym:s:screenWidth").equalTo("1280")),
            Pair.of("ym:s:lastDisplayCampaign", dimension("ym:s:lastDisplayCampaign").notDefined()),
            Pair.of("ym:s:from", dimension("ym:s:from").notDefined()),
            Pair.of("ym:s:UTMCampaign", dimension("ym:s:UTMCampaign").notDefined()),
            Pair.of("ym:s:UTMContent", dimension("ym:s:UTMContent").notDefined()),
            Pair.of("ym:s:UTMMedium", dimension("ym:s:UTMMedium").notDefined()),
            Pair.of("ym:s:UTMSource", dimension("ym:s:UTMSource").notDefined()),
            Pair.of("ym:s:UTMTerm", dimension("ym:s:UTMTerm").notDefined()),

            // параметры которые нужно заигнорить
            Pair.of("ym:s:paramsLevel1", dimension("ym:s:paramsLevel1").notDefined()),
            Pair.of("ym:s:ipAddress", dimension("ym:s:ipAddress").notDefined()),
            Pair.of("ym:s:screenOrientation", dimension("ym:s:screenOrientation").notDefined()),
            Pair.of("ym:s:productImpression", dimension("ym:s:productImpression").notDefined()),
            Pair.of("ym:s:productPurchase", dimension("ym:s:productPurchase").notDefined()),
            Pair.of("ym:u:userComment", dimension("ym:u:userComment").notDefined()),
            Pair.of("ym:s:yanPageID", dimension("ym:s:yanPageID").notDefined()),
            Pair.of("ym:s:yanBlockID", dimension("ym:s:yanBlockID").notDefined()),
            Pair.of("ym:s:yanUrl", dimension("ym:s:yanUrl").notDefined()),
            Pair.of("ym:s:yanBlockSize", dimension("ym:s:yanBlockSize").notDefined()),
            Pair.of("ym:s:publisherArticleRubric", dimension("ym:s:publisherArticleRubric").notDefined()),
            Pair.of("ym:s:publisherArticleRubric2", dimension("ym:s:publisherArticleRubric2").notDefined()),
            Pair.of("ym:s:impressionProductCategoryLevel1", dimension("ym:s:impressionProductCategoryLevel1").notDefined()),
            Pair.of("ym:s:purchaseProductCategoryLevel1", dimension("ym:s:purchaseProductCategoryLevel1").notDefined())
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
                .values(userOnTest.onUserCentricMetadataSteps().getFilters(EVENT, FILTERS, FILTER_START_SPECIAL_DATE, FILTER_END_SPECIAL_DATE))
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
                {having(on(Expression.class).build(), containsString("ym:s:ipAddress")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:paramsLevel1")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:screenOrientation")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:productImpression")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:impressionProductCategoryLevel1")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:productPurchase")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:purchaseProductCategoryLevel1")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:u:userComment")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:yanPageID")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:yanBlockID")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:yanUrl")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:yanBlockSize")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:publisherArticleRubric")), anything(), anything()},
                {having(on(Expression.class).build(), containsString("ym:s:publisherArticleRubric2")), anything(), anything()}
        });
    }
}



