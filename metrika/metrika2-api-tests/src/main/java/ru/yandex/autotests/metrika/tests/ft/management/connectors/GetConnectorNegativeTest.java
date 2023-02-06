package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.NOT_FOUND;
import static ru.yandex.autotests.metrika.errors.ManagementError.NO_OBJECT_ID;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Получение подключения (негативный)")
public class GetConnectorNegativeTest {

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);

    private static CounterFull counter;
    private static AdsConnector connector;

    @BeforeClass
    public static void init() {
        counter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        connector = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
    }

    @Test
    public void testFailGetNotExistingConnector() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorAndExpectError(counter.getId(), 0L, NO_OBJECT_ID);
    }

    @Test
    public void testFailGetConnectorForNotExistingId() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorAndExpectError(0L, connector.getConnectorId(), NOT_FOUND);
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
    }
}
