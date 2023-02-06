package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.agency;

import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V2UserAcquisitionGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonFrontParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.GrantsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.UserAcquisitionParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.ZORKA;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.TRAFFIC_SOURCES)
@Title("Агентский доступ в UA")
public class UAAgencyAccessTest {

    /**
     * Чтобы не было гонок берём не Push Sample
     */
    public static final long APP_ID = Applications.METRIKA_TEST.get(ID);

    public static final User MANAGER = Users.SUPER_LIMITED;

    public static final User GRANTEE = Users.SIMPLE_USER;

    private static final UserSteps managerSteps = UserSteps.onTesting(MANAGER);

    private static final UserSteps granteeSteps = UserSteps.onTesting(GRANTEE);

    private static final TestData.GrantCreator GRANTS = forUser(GRANTEE);

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
        GrantWrapper grantToAdd = new GrantWrapper(GRANTS.grant(GrantType.AGENCY_VIEW, ZORKA));
        managerSteps.onGrantSteps().createGrant(APP_ID, grantToAdd, new GrantsParameters().quotaIgnore());
    }

    @Test
    public void checkEmptyData() {
        CommonFrontParameters parameters = new UserAcquisitionParameters()
                .withId(APP_ID)
                // для metrika test надо взять даты побольше, чтобы были установки
                .withDate1("2020-01-01")
                .withDate2("2020-03-01")
                .withMetrics(singletonList("devices"))
                .withDimensions(singletonList("publisher"))
                .withAccuracy("1")
                .withSort("-devices,publisher");
        V2UserAcquisitionGETSchema response = granteeSteps.onTrafficSourceSteps().getReport(parameters);
        assumeThat("запрос успешен", response, expectSuccess());
        assertThat("ответ пустой", response.getData(), Matchers.emptyIterable());
    }

    @Test
    public void denyChangingTargetUser() {
        CommonFrontParameters parameters = new UserAcquisitionParameters()
                .withId(APP_ID)
                .withDate1(AppMetricaApiProperties.apiProperties().getUaStartDate())
                .withDate2(AppMetricaApiProperties.apiProperties().getUaEndDate())
                .withMetrics(singletonList("devices"))
                .withDimensions(singletonList("publisher"))
                .withAccuracy("0.05")
                .withSort("-devices,publisher")
                .withUid(178121744L);
        StatV1DataGETSchema response = granteeSteps.onReportSteps().getTableReport(parameters);
        assertThat("ошибка доступа", response, expectError(ManagementError.FORBIDDEN));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
        managerSteps.onGrantSteps().deleteGrantIgnoringResult(APP_ID, GRANTEE.get(LOGIN));
    }
}
