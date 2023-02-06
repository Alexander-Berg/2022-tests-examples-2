package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.skad;

import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.SkadnetworkV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.SKAD_TEST_APP;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.READ_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.createSkadReportDefaultParameters;

@Features(Requirements.Feature.Management.SKAD)
@Stories({
        Requirements.Story.SKAdReport.REPORT_ACCESS
})
@Title("Доступ на чтение к SKAd-отчёту")
public class SKAdReportAccessTest {

    private static final long APP_ID = SKAD_TEST_APP.get(ID);
    private static final User OWNER = SIMPLE_USER;
    private static final User ILLEGAL_USER = READ_USER;

    private static final UserSteps ownerUserSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(OWNER)
            .build();

    private static final UserSteps illegalUserSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(ILLEGAL_USER)
            .build();

    @Test
    public void testOwnerAccess() {
        SkadnetworkV1DataGETSchema report = ownerUserSteps.onReportSKAdNetworkSteps().getTableReport(
                createSkadReportDefaultParameters(APP_ID));
        assertThat("Успешный ответ без ошибок", report.getErrors(), empty());
    }

    @Test
    public void testAccessDenied() {
        SkadnetworkV1DataGETSchema report = illegalUserSteps.onReportSKAdNetworkSteps().getTableReport(
                createSkadReportDefaultParameters(APP_ID));
        assertThat("Получили ответ с кодом 403", report.getCode(), equalTo(403L));
    }
}
