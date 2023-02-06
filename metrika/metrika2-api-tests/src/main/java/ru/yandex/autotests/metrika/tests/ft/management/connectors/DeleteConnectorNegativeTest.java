package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.errors.CustomError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.lang.String.valueOf;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.errors.ManagementError.NOT_FOUND;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Удаление подключения (негативные)")
public class DeleteConnectorNegativeTest {

    private static User GUEST = SIMPLE_USER2;

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);
    private static final UserSteps stranger = new UserSteps().withUser(GUEST);

    private static CounterFull counter;
    private static AdsConnector connector;

    @BeforeClass
    public static void init() {
        counter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        connector = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        userSteps.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(
                counter.getId(),
                new GrantE()
                        .withUserLogin(GUEST.get(LOGIN))
                        .withPerm(EDIT)
        );
    }

    @Test
    public void testFailToDeleteRandomConnector() {
        stranger.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                new CustomError(403L, allOf(containsString("does not own"), containsString(valueOf(connector.getConnectorId()))))
        );
    }

    @Test
    public void testFailToDeleteInexistingConnector() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectError(counter.getId(), 1L, NOT_FOUND);
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
    }
}
