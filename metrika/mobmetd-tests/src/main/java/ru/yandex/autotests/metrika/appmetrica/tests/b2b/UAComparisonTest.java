package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V2UserAcquisitionGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.TSSource;
import ru.yandex.autotests.metrika.appmetrica.parameters.UserAcquisitionParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers.similarTo;
import static ru.yandex.autotests.metrika.appmetrica.parameters.TSSource.INSTALLATION;
import static ru.yandex.autotests.metrika.appmetrica.parameters.TSSource.NEW_INSTALLATION;
import static ru.yandex.autotests.metrika.appmetrica.parameters.TSSource.REATTRIBUTION;
import static ru.yandex.autotests.metrika.appmetrica.parameters.TSSource.REENGAGEMENT;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponses;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.TRAFFIC_SOURCES)
@Title("Источники трафика v2 (сравнение отчетов)")
@RunWith(Parameterized.class)
public final class UAComparisonTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();
    @Parameterized.Parameter
    public Long appId;

    @Parameterized.Parameter(1)
    public String eventName;

    @Parameterized.Parameter(2)
    public String date1;

    @Parameterized.Parameter(3)
    public String date2;

    @Parameterized.Parameter(4)
    public String metric;

    @Parameterized.Parameter(5)
    public String dimension;

    @Parameterized.Parameter(6)
    public TSSource source;

    @Parameterized.Parameter(7)
    public String filter;

    private IFormParameters parameters;

    @Parameterized.Parameters(name = "metr: {4}, dim: {5}, src: {6}, filter: \"{7}\"")
    public static Collection<Object[]> createParameters() {
        final List<String> metrics = ImmutableList.of(
                "devices", "clicks", "conversion", "sessions", "deeplinks", "reengagement",
                "loyalUsers", "loyalUsersPercent", "loyalUsers5", "loyalUsers10Percentage",
                "event1Count", "event1Uniqs", "event1Conversion", "event1EventsPerDevice",
                // TODO раскомментировать после релиза MOBMET-15908
                //"conversion1Count", "conversion2Uniqs", "conversion2Percentage", "conversion1CountPerDevice",
                "hasPublishers", "hasCampaigns", "hasUrlParamKeys", "hasUrlParamValues",
                "locationDisabled",
                "purchases", "payingUsers", "payingUsersPercentage",
                "revenueRUB", "revenueUSD", "averageRevenueRUBPerUser", "averageRevenueUSDPerUser",
                "ecomOrdersCount", "ecomPayingUsers", "perUserEcomOrdersCount", "ecomRevenueFiatRUB",
                "ecomRevenueInternalComponentswood", "perUserEcomRevenueFiatRUB",
                "perUserEcomRevenueInternalComponentswood", "perPayingUserEcomRevenueFiatRUB",
                "perPayingUserEcomRevenueInternalComponentswood", "perOrderEcomRevenueFiatRUB",
                "perOrderEcomRevenueInternalComponentswood", "ecomOrderCartItemQuantity",
                "perUserEcomOrderCartItemQuantity", "hasUrlParameterutm_source",
                "retentionDay5", "retentionWeek1", "retentionMonth1",
                "retentionDay5Percentage", "retentionWeek1Percentage", "retentionMonth1Percentage");
        // по name атрибутам фронт сейчас только фильтрует. В UA dimension-ы не имеют отношения к фильтрам,
        // поэтому чтобы не перегружать тесты уберём их
        final List<String> commonDimensions = ImmutableList.of(
                "publisher", "campaign", "urlParamKey", "urlParamValue",
                "regionContinent", "regionCountry", "regionArea", "regionDistrict", "regionCity", "regionCitySize",
                "buildNumberDetails", "appVersionDetails",
                //"regionContinentName", "regionCountryName", "regionAreaName",
                //"regionDistrictName", "regionCityName", "regionCitySizeName",
                "operatingSystemInfo", "osMajorVersionInfo", "operatingSystemVersionInfo",
                //"operatingSystemInfoName", "osMajorVersionInfoName", "operatingSystemVersionInfoName",
                "gender", "ageInterval",
                //"genderName", "ageIntervalName",
                "urlParameterc", "urlParameterutm_source");
        // после нового релиза
        // "urlParameter{'utm_source'}"

        return ImmutableList.<Object[]>builder()
                // User Acquisition
                .addAll(combineParams(
                        Applications.BERU.get(Application.ID),
                        "Search",
                        AppMetricaApiProperties.apiProperties().getUaStartDate(),
                        AppMetricaApiProperties.apiProperties().getUaEndDate(),
                        metrics,
                        ImmutableList.<String>builder().addAll(commonDimensions).add("installSourceType"
                        ).build(),
                        ImmutableList.of(INSTALLATION, NEW_INSTALLATION, REATTRIBUTION),
                        ImmutableList.of("", "publisher == '88234'", "campaign == '602821451791292392'",
                                "urlParamKey == 'c'")))
                // Remarketing
                .addAll(combineParams(
                        Applications.YANDEX_MONEY.get(Application.ID),
                        "Profile",
                        AppMetricaApiProperties.apiProperties().getReStartDate(),
                        AppMetricaApiProperties.apiProperties().getReEndDate(),
                        metrics,
                        commonDimensions,
                        ImmutableList.of(REENGAGEMENT),
                        ImmutableList.of("", "publisher == '30101'", "campaign == '1178949106832253502'",
                                "urlParamKey == 'referrer'")
                ))
                .build();
    }

    private static Collection<Object[]> combineParams(Long appId,
                                                      String eventName,
                                                      String date1,
                                                      String date2,
                                                      List<String> metrics,
                                                      List<String> dimensions,
                                                      List<TSSource> sources,
                                                      List<String> filters) {
        return ImmutableList.<Object[]>builder()
                .addAll( // Check all metrics
                        CombinatorialBuilder.builder()
                                .vectorValue(appId, eventName, date1, date2)
                                .values(metrics)
                                .value(any(dimensions))
                                .value(any(sources))
                                .value(any(filters))
                                .build()
                )
                .addAll( // Check all dimensions
                        CombinatorialBuilder.builder()
                                .vectorValue(appId, eventName, date1, date2)
                                .value(any(metrics))
                                .values(dimensions)
                                .value(any(sources))
                                .value(any(filters))
                                .build()
                )
                .addAll( // Check all sources
                        CombinatorialBuilder.builder()
                                .vectorValue(appId, eventName, date1, date2)
                                .value(any(metrics))
                                .value(any(dimensions))
                                .values(sources)
                                .value(any(filters))
                                .build()
                )
                .addAll( // Check all filters
                        CombinatorialBuilder.builder()
                                .vectorValue(appId, eventName, date1, date2)
                                .value(any(metrics))
                                .value(any(dimensions))
                                .value(any(sources))
                                .values(filters)
                                .build()
                )
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(appId);
        parameters = new UserAcquisitionParameters()
                .withEvents(singletonList(eventName))
                .withConversions(List.of(List.of(1L, 2L), List.of(3L)))
                .withSource(source)
                .withId(appId)
                .withDate1(date1)
                .withDate2(date2)
                .withMetrics(singletonList(metric))
                .withDimensions(singletonList(dimension))
                .withFilters(filter)
                .withAccuracy("1.00")
                // в clicks и в tracking_events семплинг работает по разному, можно вернуть после релиза
                //.withAccuracy("0.01")
                .withSort("-" + metric + "," + dimension);
    }

    @Test
    public void checkReportsMatch() {
        final V2UserAcquisitionGETSchema actual = testingSteps.onTrafficSourceSteps().getReport(parameters);
        final V2UserAcquisitionGETSchema expected = referenceSteps.onTrafficSourceSteps().getReport(parameters);

        assumeOnResponses(actual, expected);

        assertThat("отчеты совпадают", actual, similarTo(expected));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }


    private static <T> T any(List<T> list) {
        return list.iterator().next();
    }
}
