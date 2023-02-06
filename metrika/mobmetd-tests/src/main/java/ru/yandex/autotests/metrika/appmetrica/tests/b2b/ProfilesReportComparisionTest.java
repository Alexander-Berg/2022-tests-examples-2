package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.ProfilesReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.metrika.mobmet.profiles.model.ProfileAttributesResponse;
import ru.yandex.metrika.mobmet.profiles.model.ProfileBriefAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.APPMETRICA_PROD;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ProfileB2BMatchers.similarProfilesReport;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters.isIgnored;


/**
 * Проверка ручек отчёта по профилям с гистограммами
 */
@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS, Requirements.Story.METRICS
})
@Title("Profile Report B2B")
@RunWith(Parameterized.class)
public class ProfilesReportComparisionTest {

    /**
     * Обычные метрики уже тестируются по-отдельности в тесте бандла, поэтому здесь запрашиваем всё что есть на
     * странице отчёта
     */
    private static final List<String> REPORT_METRICS = ImmutableList.of(
            "ym:p:users",
            "ym:p:histogramUsersByDaysSinceLastVisit",
            "ym:p:medianDaysSinceLastVisit",
            "ym:p:histogramUsersBySessionsCount",
            "ym:p:medianSessionsCount",
            "ym:p:histogramUsersByDaysSinceFirstSession",
            "ym:p:medianDaysSinceFirstSession",
            "ym:p:histogramUsersByPushOpens",
            "ym:p:medianPushOpens",
            "ym:p:histogramUsersByCrashesCount",
            "ym:p:medianCrashesCount"
    );

    private static final Pattern CUSTOM_NUMBER_ATTRIBUTE_PATTERN = Pattern.compile("custom(Number|Counter)Attribute(\\d++)");

    private static final Double INTEGER_INTERVALS_LENGTH = 5.0;

    private static final Double FLOAT_INTERVALS_LENGTH = 2.5;


    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps onReference = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    /**
     * Чтобы тесты выполнялись побыстрее оставляем одно приложение
     */
    private static Long APPLICATION_ID = APPMETRICA_PROD.get(Application.ID);

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    @Parameterized.Parameter()
    public String attributeName;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        // Получаем список поддерживаемых группировок для приложения и для каждой генерируем параметры теста
        ProfileAttributesResponse response = onTesting.onProfileSteps().getAllAttributes(APPLICATION_ID);
        List<ProfileBriefAttribute> attributes = Stream.of(response.getCustom(), response.getPredefined(), response.getSystem())
                .flatMap(Collection::stream)
                .filter(attribute -> !isIgnored(attribute.getDimension(), "ym:p:users"))
                .collect(toList());

        return attributes
                .stream()
                .map(ProfileBriefAttribute::getDimension)
                .flatMap(dimension ->
                        isCustomNumberAttribute(dimension) ?
                                Stream.of(
                                        // Для кастомных числовых атрибутов тестируем ещё и разбиение на интервалы
                                        reportParams(dimension, 0.0),
                                        reportParams(dimension, null),
                                        reportParams(dimension, INTEGER_INTERVALS_LENGTH),
                                        reportParams(dimension, FLOAT_INTERVALS_LENGTH)
                                ) :
                                Stream.<Object[]>of(
                                        reportParams(dimension)
                                )
                )
                .collect(toList());
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APPLICATION_ID);
    }

    @Test
    @Stories({Requirements.Story.Type.TABLE})
    public void tableTest() {
        addTestParameter("Параметры", parameters.toString());

        StatV1ProfilesGETSchema testingBean = onTesting.onProfileSteps().getReport(parameters);
        StatV1ProfilesGETSchema referenceBean = onReference.onProfileSteps().getReport(parameters);

        assertThat("ответы совпадают", testingBean, similarProfilesReport(referenceBean));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static Object[] reportParams(String dimension) {
        return reportParams(dimension, 0.0);
    }

    private static Object[] reportParams(String dimension, Double intervalsLength) {
        return new Object[]{dimension, new ProfilesReportParameters()
                .withIntervalsLength(intervalsLength)
                .withDimension(dimension)
                .withId(APPLICATION_ID)
                .withDate1(apiProperties().getDefaultStartDate())
                .withDate2(apiProperties().getDefaultStartDate())
                .withMetrics(REPORT_METRICS)
                .withAccuracy("0.01")
                .withLimit(10)
                .withLang("ru")
                .withRequestDomain("ru")};
    }

    private static boolean isCustomNumberAttribute(String dimension) {
        return CUSTOM_NUMBER_ATTRIBUTE_PATTERN.matcher(dimension).find();
    }
}
