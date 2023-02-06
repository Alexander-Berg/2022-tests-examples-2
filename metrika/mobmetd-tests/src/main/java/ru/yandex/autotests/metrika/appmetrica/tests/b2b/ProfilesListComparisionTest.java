package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.profiles.model.ProfileAttributesResponse;
import ru.yandex.metrika.mobmet.profiles.model.ProfileBriefAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static java.lang.Math.max;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.APPMETRICA_PROD;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ProfileB2BMatchers.similarProfiles;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponses;
import static ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters.isIgnored;


/**
 * Проверка запроса за всеми свойствами профилей одновременно.
 */
@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS, Requirements.Story.METRICS
})
@Title("Profile List B2B")
@RunWith(Parameterized.class)
public class ProfilesListComparisionTest {

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps onReference = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    /**
     * Запрос тяжёлый, поэтому не параметризуем запрос приложениями
     */
    private static Long APPLICATION_ID = APPMETRICA_PROD.get(Application.ID);

    @Parameterized.Parameter()
    public List<String> dimensions;

    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        ProfileAttributesResponse response = onTesting.onProfileSteps().getAllAttributes(APPLICATION_ID);

        List<String> customAttrs = filterAttributes(response.getCustom());
        List<String> predefinedAttrs = filterAttributes(response.getPredefined());
        List<String> systemAttrs = filterAttributes(response.getSystem());

        // Запрашиваем за раз по одному атрибуту каждого из трёх типов
        return IntStream.range(0, max(max(customAttrs.size(), predefinedAttrs.size()), systemAttrs.size()))
                .mapToObj(i -> attrTuple(i, customAttrs, predefinedAttrs, systemAttrs))
                .map(tuple -> new Object[]{tuple})
                .collect(Collectors.toList());
    }

    private static List<String> filterAttributes(List<ProfileBriefAttribute> attributes) {
        return attributes.stream()
                .map(ProfileBriefAttribute::getDimension)
                .filter(dimension -> !isIgnored(dimension, "ym:p:users"))
                .collect(Collectors.toList());
    }

    @SafeVarargs
    private static List<String> attrTuple(int index, List<String> ...lists) {
        return Arrays.stream(lists)
                .filter(list -> index < list.size())
                .map(list -> list.get(index))
                .collect(Collectors.toList());
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APPLICATION_ID);
        parameters = new TableReportParameters()
                .withId(APPLICATION_ID)
                .withDate1(apiProperties().getDefaultStartDate())
                .withDate2(apiProperties().getDefaultStartDate())
                .withDimensions(dimensions)
                .withMetric("ym:p:users")
                // берём семплинг повыше из-за METRIQA-4170
                // после исправления проблем в ClickHouse можно вернуть 0.05 ил 0.1
                .withAccuracy("0.5")
                .withLimit(10)
                .withLang("ru")
                .withRequestDomain("ru");
    }

    @Test
    @Stories({Requirements.Story.Type.TABLE})
    public void test() {
        addTestParameter("Параметры", parameters.toString());

        StatV1DataGETSchema testingBean = onTesting.onProfileSteps().getListReport(parameters);
        StatV1DataGETSchema referenceBean = onReference.onProfileSteps().getListReport(parameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, similarProfiles(referenceBean));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
