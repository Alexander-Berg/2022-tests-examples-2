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
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportType;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportTypes;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.changeTestCaseTitle;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.utils.ReportTypes.TABLE;

@Features(Requirements.Feature.DATA)
@Title("B2B на отобранных вручную параметрах запросов с сегментами")
@RunWith(ParallelizedParameterized.class)
public class SegmentsB2BTest {

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
                .addAll(createParams("MOBMET-15241: funnels request, multiple dimensions",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.01")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:uf:segment,ym:uf:regionCountry")
                                .withMetrics(ImmutableList.of(
                                        "ym:uf:users",
                                        "ym:uf:devices",
                                        "ym:uf:devicesInStep1",
                                        "ym:uf:devicesInStep2",
                                        "ym:uf:devicesInStep3"))
                                .withFunnelPattern("" +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and eventLabel=='Кредиты. Переход из шапки к кредитному блоку' and isForeground=='yes') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and eventLabel=='Кредиты. Отправка заявки' and exists(paramsLevel1=='Источник' and paramsLevel2=='Карточка') and isForeground=='yes') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and (eventLabel=='Кредиты. Кредитный визард')) and isForeground=='yes')")
                                .withSegments("" +
                                        "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                        "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                        "\"ym:uf:gender=='male' and ym:uf:date>='2021-09-24' and ym:uf:date<='2021-09-25'\"]")
                                .withLimit(10)))
                .addAll(createParams("MOBMET-15241: include undefined true",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.01")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:uf:segment")
                                .withMetrics(ImmutableList.of(
                                        "ym:uf:users",
                                        "ym:uf:devices",
                                        "ym:uf:devicesInStep1",
                                        "ym:uf:devicesInStep2",
                                        "ym:uf:devicesInStep3"))
                                .withFunnelPattern("" +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and eventLabel=='Кредиты. Переход из шапки к кредитному блоку' and isForeground=='yes') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and eventLabel=='Кредиты. Отправка заявки' and exists(paramsLevel1=='Источник' and paramsLevel2=='Карточка') and isForeground=='yes') " +
                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and (eventLabel=='Кредиты. Кредитный визард')) and isForeground=='yes')")
                                .withSegments("" +
                                        "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                        "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                        "\"ym:uf:gender=='male' and ym:uf:date>='2021-09-24' and ym:uf:date<='2021-09-25'\", " +
                                        "\"ageInterval=='25'\"]")
                                .withIncludeUndefined(true)
                                .withLimit(10)))
                .addAll(createParams("MOBMET-15241: subquery request",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.01")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:s:segment")
                                .withMetrics(ImmutableList.of("ym:s:users", "ym:s:sessions"))
                                .withSegments("" +
                                        "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                        "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                        "\"ym:uf:gender=='male' and ym:uf:date>='2021-09-24' and ym:uf:date<='2021-09-25'\"]")
                                .withLimit(10)))
                .addAll(createParams("MOBMET-15241: no namespace in parameters",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.01")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:s:segment")
                                .withMetrics(ImmutableList.of("ym:s:users", "ym:s:sessions"))
                                .withSegments("" +
                                        "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                        "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                        "\"gender=='male' and date>='2021-10-11' and date<='2021-10-14'\"]")
                                .withLimit(10)))
                .addAll(createParams("MOBMET-15241: subquery request with segmentation",
                        ImmutableList.of(TABLE),
                        new TableReportParameters()
                                .withId(Applications.AUTO_RU)
                                .withAccuracy("0.01")
                                .withDate1("2021-10-10")
                                .withDate2("2021-10-17")
                                .withDimension("ym:s:segment")
                                .withMetrics(ImmutableList.of("ym:s:users", "ym:s:sessions"))
                                .withFilters("" +
                                        "exists ym:ge:device with (eventType=='EVENT_START' and " +
                                        "specialDefaultDate>='2021-10-07' and specialDefaultDate<='2021-10-09') " +
                                        "and ageInterval=='25'")
                                .withSegments("" +
                                        "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                        "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                        "\"ym:s:gender=='male' and ym:s:date>='2021-09-24' and ym:s:date<='2021-09-25'\"]")
                                .withLimit(10)))
                        .addAll(createParams("MOBMET-15241: join bundle",
                                ImmutableList.of(TABLE),
                                new TableReportParameters()
                                        .withId(Applications.AUTO_RU)
                                        .withAccuracy("0.01")
                                        .withDate1("2021-10-10")
                                        .withDate2("2021-10-17")
                                        .withDimension("ym:u:segment")
                                        .withMetrics(ImmutableList.of("ym:u:users", "ym:u:sessions"))
                                        .withSegments("" +
                                                "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                                "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                                "\"ym:u:gender=='male'\"]")
                                        .withLimit(10)))
                        .addAll(createParams("MOBMET-15241: fixed join bundle",
                                ImmutableList.of(TABLE),
                                new TableReportParameters()
                                        .withId(Applications.AUTO_RU)
                                        .withAccuracy("0.01")
                                        .withDate1("2021-10-10")
                                        .withDate2("2021-10-17")
                                        .withDimension("ym:ce2:segment")
                                        .withMetrics(ImmutableList.of("ym:ce2:users,ym:ce2:eventsPerUser"))
                                        .withSegments("" +
                                                "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                                "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                                "\"eventLabel=='ad_requested'\", " +
                                                "\"gender=='male'\"]")
                                        .withLimit(10)))
                        .addAll(createParams("MOBMET-15241: filter by segment attribute (don't show that to frontend)",
                                ImmutableList.of(TABLE),
                                new TableReportParameters()
                                        .withId(Applications.AUTO_RU)
                                        .withAccuracy("0.01")
                                        .withDate1("2021-10-10")
                                        .withDate2("2021-10-17")
                                        .withMetrics(ImmutableList.of("ym:u:users", "ym:u:sessions"))
                                        .withFilters("segment=='1'")
                                        .withSegments("" +
                                                "[\"exists ym:i:device with (campaign=='8' and specialDefaultDate>='2015-01-01')\", " +
                                                "\"exists ym:d:device with ((regionCountry=='225'))\", " +
                                                "\"ym:u:gender=='male'\"]")
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

    private static List<Object[]> createParams(String title, List<ReportType<?>> reportType, IFormParameters... parameters) {
        return reportType.stream().map(rt -> toArray(title, rt, makeParameters().append(parameters))).collect(Collectors.toList());
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
