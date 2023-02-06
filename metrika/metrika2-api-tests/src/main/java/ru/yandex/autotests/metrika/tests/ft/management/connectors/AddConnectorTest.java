package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Создание подключений")
public class AddConnectorTest {

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);

    private static long counterId;
    private static long otherCounterId;

    private static AdsConnector connector;
    private static AdsConnector dubbedConnector;

    @BeforeClass
    public static void init() {
        counterId = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
        otherCounterId = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();

        connector = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counterId);
        dubbedConnector = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectSuccess(otherCounterId, connector);
    }

    @Test
    public void testAddNewConnector() {
        List<AdsConnector> connectors = userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counterId, "", "");
        assertThat(
                "новое подключение успешно созданно",
                connectors,
                allOf(
                        iterableWithSize(1),
                        hasItem(beanEquivalent(connector))
                )
        );
    }

    @Test
    public void testAddExistingConnectorToCounter() {
        List<AdsConnector> connectors = userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(otherCounterId, "", "");
        assertThat(
                "существующее подключение успешно добавленно к счетчику " + otherCounterId,
                connectors,
                allOf(
                        iterableWithSize(1),
                        hasItem(beanEquivalent(dubbedConnector))
                )
        );
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(otherCounterId, connector.getConnectorId());
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counterId, connector.getConnectorId());

        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(otherCounterId);
    }
}
