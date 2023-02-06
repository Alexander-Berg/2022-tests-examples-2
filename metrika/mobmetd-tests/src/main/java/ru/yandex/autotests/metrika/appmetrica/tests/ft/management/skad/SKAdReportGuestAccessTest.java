package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.skad;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.SkadnetworkV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.SKAD_TEST_APP;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.createSkadReportDefaultParameters;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

@Features(Requirements.Feature.Management.SKAD)
@Stories({
        Requirements.Story.SKAdReport.REPORT_ACCESS
})
@Title("Гостевой доступ на чтение к SKAd-отчёту")
@RunWith(Parameterized.class)
public class SKAdReportGuestAccessTest {

    private static final long APP_ID = SKAD_TEST_APP.get(ID);
    private static final User OWNER = SIMPLE_USER;
    private static final User GUEST = SIMPLE_USER_2;

    private static final UserSteps ownerUserSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(OWNER)
            .build();

    private static final UserSteps guestUserSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(GUEST)
            .build();

    @Parameterized.Parameter()
    public GrantWrapper grantToAdd;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[]{new GrantWrapper(forUser(GUEST).grant(VIEW))},
                new Object[]{new GrantWrapper(forUser(GUEST).grant(EDIT))}
        );
    }

    @Before
    public void setUp() throws Exception {
        ownerUserSteps.onGrantSteps().createGrant(APP_ID, grantToAdd);
    }

    @Test
    public void testGuestAccess() {
        SkadnetworkV1DataGETSchema report = guestUserSteps.onReportSKAdNetworkSteps().getTableReport(
                createSkadReportDefaultParameters(APP_ID));
        assertThat("Успешный ответ без ошибок", report.getErrors(), empty());
    }

    @After
    public void tearDown() throws Exception {
        ownerUserSteps.onGrantSteps().deleteGrantIgnoringResult(APP_ID, GUEST.get(LOGIN));
    }
}
