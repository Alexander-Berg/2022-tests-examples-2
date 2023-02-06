package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParameters;
import ru.yandex.autotests.irt.testutils.rules.parameters.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.*;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportType;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportTypes;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.changeTestCaseTitle;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.utils.ReportTypes.*;

/**
 * Created by konkov on 05.07.2016.
 */
@Features(Requirements.Feature.DATA)
@Title("B2B на отобранных вручную параметрах запросов")
@RunWith(ParallelizedParameterized.class)
public class ParticularB2bTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps onReference = UserSteps.builder()
            .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(1)
    public ReportType<?> reportType;

    @Parameterized.Parameter(2)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(createParams("MOBMET-6344: Не строятся Аудитории с фильтром по параметру события",
                        BYTIME, new BytimeReportParameters()
                                .withId(Applications.YANDEX_KEYBOARD)
                                .withAccuracy("0.1")
                                .withDate1("2017-07-01")
                                .withDate2("2017-07-07")
                                .withMetrics(of("ym:u:users"))
                                .withFilters("exists ym:ce:device with (exists (ym:ce:paramsLevel1=='Developer Info') AND ym:ce:eventLabel=='All Devices Statistics')")))
                .addAll(createParams("MOBMET-7098: В график установок не попадают события",
                        TABLE, new TableReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.01")
                                .withDate1("2017-11-01")
                                .withDate2("2017-11-01")
                                .withMetric("ym:ts:installDevices")
                                .withDimension("ym:ts:urlParamKey")
                                .withFilters("exists (ym:ts:urlParamKey == 'utm_source') and ym:ts:urlParamKey == 'utm_medium'")))
                // exists-ы в стандартном апи
                .addAll(createParams("exists по девайсу",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME, TREE), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("0.1")
                                .withDate1("2018-10-01")
                                .withDate2("2018-10-01")
                                .withMetric("ym:ce:clientEvents")
                                .withDimension("ym:ce:eventLabel")
                                .withFilters("exists ym:i:device with (publisher=='0' and specialDefaultDate>='2015-01-01')")))
                .addAll(createParams("exists по пользователю",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME, TREE), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("0.1")
                                .withDate1("2018-10-01")
                                .withDate2("2018-10-01")
                                .withMetric("ym:ce:clientEvents")
                                .withDimension("ym:ce:eventLabel")
                                .withFilters("exists ym:ge:user with (eventType=='EVENT_START' and specialDefaultDate>='2018-10-02' and specialDefaultDate<='2018-10-03')")))
                .addAll(createParams("exists по сессии",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME, TREE), new TableReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.01")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withMetric("ym:u:activeUsers")
                                .withDimension("ym:u:date")
                                .withFilters("exists ym:ce:session with (eventLabel=='application.settings')")))
                .addAll(createParams("exists по паре атрибутов",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME, TREE), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("2020-03-01")
                                .withDate2("2020-03-01")
                                .withMetric("ym:ce2:usersWithEvent")
                                .withDimension("ym:ce2:eventLabel")
                                .withFilters("exists ym:p:device,ym:p:profileOrigin with (customNumberAttribute1379>'1')")
                                .withSort("-ym:ce2:usersWithEvent")))
                .addAll(createParams("Вложенные exists-ы",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME, TREE), new TableReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.01")
                                .withDate1("2020-03-01")
                                .withDate2("2020-03-01")
                                .withMetric("ym:ce:clientEvents")
                                .withDimension("ym:ce:eventLabel")
                                .withFilters("exists ym:u:device with (exists ym:i:device with (publisher=='0' and specialDefaultDate<='2020-02-01' and specialDefaultDate>='2020-01-01'))")
                                .withSort("-ym:ce:clientEvents")))
                // базовые exist-ы в кастомных ручка
                .addAll(createParams("exists по девайсу в UA",
                        USER_ACQUISITION, new UserAcquisitionParameters()
                                .withId(Applications.ANDROID_APP)
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withDimension("campaign")
                                .withMetric("clicks")
                                .withSort("-clicks")
                                .withAccuracy("1")
                                //.withAccuracy("0.2")
                                .withFilters("exists ym:i:device with (publisher=='0' and specialDefaultDate>='2020-01-01')")))
                .addAll(createParams("exists по девайсу в CA",
                        COHORT, new CohortAnalysisParameters()
                                .withId(Applications.AUTO_RU)
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-21")
                                .withAccuracy("0.01")
                                .withCohortType(CACohortType.installationDate())
                                .withMetric(CAMetric.DEVICES)
                                .withRetention(CARetention.CLASSIC)
                                .withGroup(CAGroup.DAY)
                                .withConversion(CAConversion.sessionStart())
                                .withFilter("exists ym:pc:device with (actionType=='send' and (campaignOrGroup=='181222.null') and specialDefaultDate>='2020-01-01' and specialDefaultDate<='today')")))
                .addAll(createParams("exists по девайсу в отчёте по профилям",
                        ImmutableList.of(PROFILE_REPORT, PROFILE_LIST), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("0.1")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withMetric("ym:p:users")
                                .withDimension("ym:p:regionCountry")
                                .withSort("-ym:p:regionCountry")
                                .withFilters("exists ym:i:device with (publisher=='0' and specialDefaultDate>='2020-01-01')")))
                .addAll(createParams("parentIds в DRILLDOWN",
                        DRILLDOWN, new DrillDownReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.01")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withMetric("ym:ce2:users,ym:ce2:devices,ym:ce2:clientEvents")
                                .withDimension("ym:ce2:eventLabel,ym:ce2:paramsLevel1,ym:ce2:paramsLevel2,ym:ce2:paramsLevel3,ym:ce2:paramsLevel4,ym:ce2:paramsLevel5")
                                .withParentIds(Collections.singletonList("application.start-session"))
                                .withSort("-ym:ce2:clientEvents")))
                .addAll(createParams("MOBMET-9074: table filter by EventName",
                        TABLE, new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD.get(Application.ID))
                                .withAccuracy("1")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withMetric("ym:ce2:usersWithEvent,norm(ym:ce2:usersWithEvent),ym:ce2:fgEvents," +
                                        "norm(ym:ce2:fgEvents),ym:ce2:eventsPerUser,ym:ce2:usersPercent," +
                                        "ym:ce2:devicesWithEvent,norm(ym:ce2:devicesWithEvent),ym:ce2:allEvents," +
                                        "norm(ym:ce2:allEvents),ym:ce2:eventsPerDevice,ym:ce2:devicesPercent," +
                                        "ym:ce2:hasParamsLevel1")
                                .withDimension("ym:ce2:eventLabel")
                                .withFilters("ym:ce2:eventLabel=@'dashboard'")
                                .withSort("-ym:ce2:usersWithEvent")))
                .addAll(createParams("MOBMET-9144: profile system attributes comparison",
                        TABLE, new TableReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.01")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withMetric("ym:u:activeUsers,ym:u:activeUsersPercentage,ym:u:newUsers,ym:u:newUsersPercentage,ym:u:newUsersShare")
                                .withDimension("ym:u:ageInterval")
                                .withFilters("exists ym:d:device with (sessionsCount>='1' and sessionsCount<='10' and crashesCount>='0' and crashesCount<='5')")
                                .withSort("-ym:u:activeUsers")))
                .addAll(createParams("MOBMET-9254: exists в namespace без дат с date_dimension=Receive",
                        ImmutableList.of(TABLE), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("0.5")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withDateDimension("Receive")
                                .withMetric("ym:i:devices")
                                .withDimension("ym:i:regionArea")
                                .withFilters("exists ym:p:device with (regionCountry=='225')")))
                .addAll(createParams("MOBMET-9254: для параметра date_dimension отсутствие значения и 'Default' эквивалентны",
                        ImmutableList.of(TABLE, BYTIME, DRILLDOWN), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withDateDimension("Default")
                                .withMetric("ym:ge:users")
                                .withDimension("ym:ge:regionArea")))
                .addAll(createParams("MOBMET-9829: exists filter by tuple in FixedJoin",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("2020-03-20")
                                .withDate2("2020-03-20")
                                .withMetric("ym:ce2:users")
                                .withDimension("ym:ce2:eventLabel,ym:ce2:paramsLevel1")
                                .withFilters("eventLabel=='Screen applications' and exists(paramsLevel1=='Number of applications')")
                                .withSort("-ym:ce2:users")))
                .addAll(createParams("MOBMET-9829: flat filter by tuple in FixedJoin",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("2019-03-20")
                                .withDate2("2019-03-20")
                                .withMetric("ym:ce2:users,ym:ce2:usersWithEvent,norm(ym:ce2:usersWithEvent),ym:ce2:eventsPerUser,ym:ce2:usersPercent")
                                .withDimension("ym:ce2:eventLabel,ym:ce2:paramsLevel1")
                                .withFilters("eventLabel=='Screen applications' and paramsLevel1=='Number of applications'")
                                .withSort("-ym:ce2:users")))
                .addAll(createParams("MOBMET-9829: test another type of tuples",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("2019-03-20")
                                .withDate2("2019-03-20")
                                .withMetric("ym:ce2:users,ym:ce2:usersWithEvent,norm(ym:ce2:usersWithEvent),ym:ce2:eventsPerUser,ym:ce2:usersPercent")
                                .withDimension("ym:ce2:eventLabel,ym:ce2:paramsLevel1")
                                .withFilters("exists ym:p:device,ym:p:profileOrigin with (customNumberAttribute1379>'1')")
                                .withSort("-ym:ce2:users")))
                .addAll(createParams("MOBMET-9867: negative filter in fixed join",
                        ImmutableList.of(TABLE, DRILLDOWN, BYTIME), new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("2019-03-20")
                                .withDate2("2019-03-20")
                                .withMetric("ym:ce2:users,ym:ce2:usersWithEvent,norm(ym:ce2:usersWithEvent),ym:ce2:eventsPerUser,ym:ce2:usersPercent")
                                .withDimension("ym:ce2:eventLabel,ym:ce2:paramsLevel1")
                                .withFilters("not(eventLabel=='Screen applications')")
                                .withSort("-ym:ce2:users")))
                .addAll(createParams("MOBMET-10730: parentId by attribute with tuple in join",
                        ImmutableList.of(DRILLDOWN), new DrillDownReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("2019-08-20")
                                .withDate2("2019-08-20")
                                .withMetric("ym:ts:devices")
                                .withDimension("ym:ts:urlParamKey,ym:ts:urlParamValue")
                                .withParentIds(Collections.singletonList("from"))
                                .withSort("-ym:ts:devices")))
                .addAll(createParams("MOBMET-11814: aggregates in tuple attributes",
                        USER_ACQUISITION, new UserAcquisitionParameters()
                                .withId(Applications.YANDEX_MUSIC)
                                .withDate1(AppMetricaApiProperties.apiProperties().getUaStartDate())
                                .withDate2(AppMetricaApiProperties.apiProperties().getUaEndDate())
                                .withDimension("urlParamKey")
                                .withMetric("devices,clicks,deeplinks,hasUrlParamValues")
                                .withSort("-devices")
                                //.withAccuracy("0.01")
                                .withAccuracy("1.00")))
                .addAll(createParams("MOBMET-10730: parentId by attribute with tuple in join",
                        ImmutableList.of(TABLE), new TableReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.01")
                                .withDate1("2020-03-10")
                                .withDate2("2020-03-10")
                                .withMetric("ym:ts:devices")
                                .withDimension("ym:ts:urlParameterutm_source")
                                .withSort("-ym:ts:devices")))
                .addAll(createParams("MOBMET-12248: query should be fine",
                        TABLE, new TableReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.01")
                                .withDate1("2020-03-01")
                                .withDate2("2020-03-07")
                                .withMetric("ym:s:sessions")
                                .withDimension("ym:s:date")
                                .withFilters("not exists ym:i:device with (specialDefaultDate>='2020-02-27' and specialDefaultDate<='2020-02-27') and " +
                                        "exists ym:i:device with (specialDefaultDate>='2020-02-28' and specialDefaultDate<='2020-02-28')")
                                .withSort("-ym:s:sessions")))
                .addAll(createParams("MOBMET-12557: using several attributes with parameterization",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-04-29")
                                .withDate2("2020-05-12")
                                .withMetric("ym:ts:advInstallDevices")
                                .withDimension("ym:ts:urlParameter<url_parameter_key_2>,ym:ts:urlParameter<url_parameter_key>")
                                .withFilters("ym:ts:urlParameter<url_parameter_key_1>=='true'")
                                .withSort("-ym:ts:advInstallDevices"),
                        FreeFormParameters.makeParameters()
                                .append("url_parameter_key", "iad-adgroup-id")
                                .append("url_parameter_key_1", "iad-attribution")
                                .append("url_parameter_key_2", "iad-campaign-id")))
                .addAll(createParams("MOBMET-12557: using several attributes with parameterization",
                        ImmutableList.of(USER_ACQUISITION),
                        new UserAcquisitionParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-04-29")
                                .withDate2("2020-05-12")
                                .withMetric("devices,clicks,deeplinks")
                                .withDimension("urlParameter{'iad-campaign-id'},urlParameter{'iad-adgroup-id'}")
                                .withFilters("urlParameter{'iad-attribution'}=='true'")
                                .withSort("-devices")))
                .addAll(createParams("MOBMET-12557: using several metrics with parameterization",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.EDADEAL)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withMetric("ym:ts:advInstallDevices,ym:ts:urlParamValues<url_parameter_key>,ym:ts:urlParamValues<url_parameter_key_2>,ym:ts:urlParamValuesconversion_metric")
                                .withDimension("ym:ts:urlParametercampaign_name,ym:ts:urlParameter<url_parameter_key_1>")
                                .withFilters("ym:ts:urlParamValues<url_parameter_key_2>>2")
                                .withSort("-ym:ts:advInstallDevices"),
                        FreeFormParameters.makeParameters()
                                .append("url_parameter_key", "campaign_type")
                                .append("url_parameter_key_1", "campaign_id")
                                .append("url_parameter_key_2", "ad_event_id")))
                .addAll(createParams("MOBMET-12557: bytime",
                        ImmutableList.of(BYTIME),
                        new BytimeReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withRowIds("[[\"69378\",\"true\"]]")
                                .withMetric("ym:ts:advInstallDevices")
                                .withDimension("ym:ts:publisher,ym:ts:urlParameter<url_parameter_key>,ym:ts:urlParameter<url_parameter_key_1>")
                                .withFilters("publisher=='69378'")
                                .withSort("-ym:ts:advInstallDevices"),
                        FreeFormParameters.makeParameters()
                                .append("url_parameter_key", "iad-attribution")
                                .append("url_parameter_key_1", "iad-campaign-id")))
                .addAll(createParams("MOBMET-12557: drilldown expand metric",
                        ImmutableList.of(DRILLDOWN),
                        new DrillDownReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withParentIds(Arrays.asList("69378", "true"))
                                .withMetric("ym:ts:advInstallDevices,ym:ts:urlParamValues<url_parameter_key>")
                                .withDimension("ym:ts:publisher,ym:ts:urlParameter<url_parameter_key>,ym:ts:urlParameter<url_parameter_key_1>")
                                .withFilters("publisher=='69378'")
                                .withSort("-ym:ts:advInstallDevices"),
                        FreeFormParameters.makeParameters()
                                .append("url_parameter_key", "iad-attribution")
                                .append("url_parameter_key_1", "iad-campaign-id")))
                .addAll(createParams("MOBMET-12557: check profiles regression",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.APPMETRICA_PROD)
                                .withAccuracy("1")
                                .withDate1("today")
                                .withDate2("today")
                                .withMetric("ym:p:users")
                                .withDimension("ym:p:customNumberAttribute1379AsIntervals<pca_integer_intervals>WithLength<pca_intervals_length>")
                                .withSort("-ym:p:users"),
                        FreeFormParameters.makeParameters()
                                .append("pca_integer_intervals", "true")
                                .append("pca_intervals_length", "4.0")))
                .addAll(createParams("MOBMET-12791: max subquery depth on mobgiga",
                        ImmutableList.of(TABLE), new TableReportParameters()
                                .withId(Applications.YANDEX_METRO)
                                .withAccuracy("0.1")
                                .withDate1("2020-06-05")
                                .withDate2("2020-06-05")
                                .withMetric("ym:s:users")
                                .withDimension("ym:s:mobileDeviceBranding")
                                .withFilters("exists ym:u:device with (exists ym:s:device with ((operatingSystemInfo=='android')))")))
                .addAll(createParams("MOBMET-12890: parametrization in metric filters",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withMetric("ym:ts:urlParamValues<url_parameter_key>[ym:ts:urlParametercampaign_id=='6465933565']"),
                        FreeFormParameters.makeParameters().append("url_parameter_key", "ad_type")))
                .addAll(createParams("MOBMET-12890: parametrization in metric filters",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withMetric("ym:ts:urlParamValuesad_type[ym:ts:urlParametercampaign_id=='6465933565']")))
                .addAll(createParams("MOBMET-12890: parametrization in metric filters",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withFilters("exists ym:i:device with (ym:i:urlParametercampaign_id=='6465933565')")
                                .withMetric("ym:ts:urlParamValues<url_parameter_key>"),
                        FreeFormParameters.makeParameters().append("url_parameter_key", "ad_type")))
                .addAll(createParams("MOBMET-12890: parametrization in metric filters",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withMetric("ym:ts:urlParamValues<url_parameter_key>[ym:ts:urlParameter<url_parameter_key>=='6465933565']"),
                        FreeFormParameters.makeParameters().append("url_parameter_key", "campaign_id")))
                .addAll(createParams("MOBMET-13163: session funnels",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.EDADEAL)
                                .withAccuracy("0.1")
                                .withDate1("2020-07-07")
                                .withDate2("2020-07-14")
                                .withDimension("ym:sf:regionCity")
                                .withMetrics(ImmutableList.of(
                                        "ym:sf:users", "ym:sf:sessions",
                                        "ym:sf:devicesInStep1", "ym:sf:devicesInStep2",
                                        "ym:sf:sessionsInStep1", "ym:sf:sessionsInStep2"))
                                .withFilters("regionCountry=='225'")
                                .withFunnelPattern("" +
                                        "cond(ym:sft, eventType=='EVENT_CLIENT' AND eventLabel=='TutorialScreenAppear') " +
                                        "next cond(ym:sft, eventType=='EVENT_CLIENT' AND eventLabel=='MainScreenAppear')")
                                .withFunnelRestriction("eventType=='EVENT_CLIENT'")
                                .withLimit(10)))
                .addAll(createParams("MOBMET-13163: user funnels",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.EDADEAL)
                                .withAccuracy("0.1")
                                .withDate1("2020-07-07")
                                .withDate2("2020-07-14")
                                .withDimension("ym:uf:regionCity")
                                .withMetrics(ImmutableList.of(
                                        "ym:uf:users",
                                        "ym:uf:devices",
                                        "ym:uf:devicesInStep1",
                                        "ym:uf:devicesInStep2"))
                                .withFilters("regionCountry=='225'")
                                .withFunnelPattern("" +
                                        "cond(ym:uft, eventType=='EVENT_NOTIFICATION' AND actionType=='open' AND campaignInfo=='group.2167') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' AND eventLabel=='TutorialScreenAppear') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' AND eventLabel=='MainScreenAppear')")
                                .withLimit(10)))
                .addAll(createParams("MOBMET-15335: user funnels with any event on first step",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.1")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:uf:regionCountry")
                                .withMetrics(ImmutableList.of(
                                        "ym:uf:users",
                                        "ym:uf:devices",
                                        "ym:uf:devicesInStep1",
                                        "ym:uf:devicesInStep2",
                                        "ym:uf:devicesInStep3"))
                                .withFunnelPattern("" +
                                        "cond(ym:uft, isAnyEvent=='yes' and sessionType=='foreground') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and " +
                                        "             (eventLabel=='Кредиты. Кредитный визард' and exists(paramsLevel1=='Тап на кнопку Я найду другой автомобиль') or " +
                                        "              eventLabel=='Кредиты. Личный кабинет' and exists(paramsLevel1=='Тап на Выбрать другой автомобиль') or " +
                                        "              eventLabel=='Кредиты. Полная кредитная анкета' and exists(paramsLevel1=='Тап на кнопку Я найду другой автомобиль')) and " +
                                        "             sessionType=='foreground') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and eventLabel=='Переход в расширенный поиск (FAB)' and sessionType=='foreground')+")
                                .withLimit(10)))
                .addAll(createParams("MOBMET-12557: using several attributes with escaping parameterization",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-04-29")
                                .withDate2("2020-05-12")
                                .withMetric("ym:ts:advInstallDevices")
                                .withDimension("ym:ts:urlParameter{'iad-campaign-id'},ym:ts:urlParameter{'iad-adgroup-id'}")
                                .withFilters("ym:ts:urlParameter{'iad-attribution'}=='true'")
                                .withSort("-ym:ts:advInstallDevices")))
                .addAll(createParams("MOBMET-12557: using several metrics with escaping parameterization",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.EDADEAL)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withMetric("ym:ts:advInstallDevices,ym:ts:urlParamValues{'campaign_type'},ym:ts:urlParamValues{'campaign_name'},ym:ts:urlParamValuesconversion_metric")
                                .withDimension("ym:ts:urlParametercampaign_name,ym:ts:urlParameter{'campaign_id'}")
                                .withFilters("ym:ts:urlParamValues{'ad_event_id'}>2")
                                .withSort("-ym:ts:advInstallDevices")))
                .addAll(createParams("MOBMET-12557: bytime escaping parametrization",
                        ImmutableList.of(BYTIME),
                        new BytimeReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withRowIds("[[\"69378\",\"true\"]]")
                                .withMetric("ym:ts:advInstallDevices")
                                .withDimension("ym:ts:publisher,ym:ts:urlParameter{'iad-attribution'},ym:ts:urlParameter{'iad-campaign-id'}")
                                .withFilters("publisher=='69378'")
                                .withSort("-ym:ts:advInstallDevices")))
                .addAll(createParams("MOBMET-12557: drilldown expand metric escaping parametrization",
                        ImmutableList.of(DRILLDOWN),
                        new DrillDownReportParameters()
                                .withId(Applications.KINOPOISK)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-14")
                                .withParentIds(Arrays.asList("69378", "true"))
                                .withMetric("ym:ts:advInstallDevices,ym:ts:urlParamValues{'iad-attribution'}")
                                .withDimension("ym:ts:publisher,ym:ts:urlParameter{'iad-attribution'},ym:ts:urlParameter{'iad-campaign-id'}")
                                .withFilters("publisher=='69378'")
                                .withSort("-ym:ts:advInstallDevices")))
                .addAll(createParams("MOBMET-15762: bytime for tuples",
                        ImmutableList.of(BYTIME),
                        new BytimeReportParameters()
                                .withId(Applications.IGOOODS)
                                .withAccuracy("1")
                                .withDate1("2022-02-01")
                                .withDate2("2022-02-05")
                                .withRowIds("[[\"auchan\"],[\"babylon\"],[\"lenta\",\"true\"]]")
                                .withMetric("ym:ce2:sumParamValuesPerDevice{'price'},ym:ce2:sumParamValuesPerSession{'price'},ym:ce2:medianParamValue{'price'},ym:ce2:allClientSessions")
                                .withDimension("ym:ce2:paramValue{'shop group'},ym:ce2:paramValue{'asap'}"),
                        FreeFormParameters.makeParameters()
                                .append("url_parameter_key", "iad-attribution")
                                .append("url_parameter_key_1", "iad-campaign-id")))
                .addAll(createParams("MOBMET-16119: неправильные срабатывания оптимизатора запросов крэшей",
                        TABLE, new TableReportParameters()
                                .withId(Applications.ZEN_APP)
                                .withAccuracy("1")
                                .withDate1("2022-06-20")
                                .withDate2("2022-06-20")
                                .withMetric("ym:cr2:crashes")
                                .withDimension("ym:cr2:crashGroupObj")
                                .withFilters("ym:cr2:operatingSystemInfo=='android' and exists ym:ce:device with (eventLabel=='zen brief_editor')")
                                .withSort("-ym:cr2:crashes")
                                .withLimit(10)))
                .build();
    }

    @IgnoreParameters.Tag(name = "known_issues")
    public static Collection ignoredParamsAsKnownIssues() {
        return asList(new Object[][]{});
    }

    @Before
    public void setup() {
        changeTestCaseTitle(title);
        setCurrentLayerByApp(ReportTypes.extractAppId(parameters));
    }

    @Test
    @IgnoreParameters(reason = "Известные проблемы", tag = "known_issues")
    public void check() {
        reportType.assertB2b(onTesting, onReference, parameters);
    }

    private static List<Object[]> createParams(String title, ReportType<?> reportType, IFormParameters... parameterses) {
        return Collections.singletonList(toArray(title, reportType, makeParameters().append(parameterses)));
    }

    private static List<Object[]> createParams(String title, List<ReportType<?>> reportType, IFormParameters... parameterses) {
        return reportType.stream().map(rt -> toArray(title, rt, makeParameters().append(parameterses))).collect(Collectors.toList());
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
