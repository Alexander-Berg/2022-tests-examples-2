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

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Получение активных подключений для счетчика")
public class GetConnectorsForCounterTest {

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);

    private static CounterFull counter;
    private static List<AdsConnector> connectors = new ArrayList<>();

    @BeforeClass
    public static void init() {
        counter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        connectors.add(userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId()));
        connectors.add(userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId()));
        connectors.add(userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId()));
    }

    @Test
    public void testGetAllConnectors() {
        assertThat(
                "Получаем все активные подключения для счетчика " + counter.getId(),
                userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "", ""),
                allOf(
                        iterableWithSize(connectors.size()),
                        hasItems(beanEquivalent(connectors.get(0)), beanEquivalent(connectors.get(1)), beanEquivalent(connectors.get(2)))
                )
        );
    }

    @Test
    public void testGetConnectorsByFilter() {
        String filter = connectors.get(0).getName().split("_")[1];
        assertThat(
                "Получаем подключения для счетчика " + counter.getId() + " по фильтру " + filter,
                userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "", filter),
                allOf(
                        iterableWithSize(1),
                        hasItem(beanEquivalent(connectors.get(0)))
                )
        );
    }

    @Test
    public void testGetConnectorsByPlatformGoogle() {
        assertThat(
                "Получаем подключения для счетчика " + counter.getId() + " по платформе GOOGLE",
                userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "google", ""),
                allOf(
                        iterableWithSize(connectors.size()),
                        hasItems(beanEquivalent(connectors.get(0)), beanEquivalent(connectors.get(1)), beanEquivalent(connectors.get(2)))
                )
        );
    }

    @Test
    public void testGetConnectorsByPlatformFacebook() {
        assertThat(
                "Получаем подключения для счетчика " + counter.getId() + " по платформе Facebook",
                userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "facebook", ""),
                iterableWithSize(0)

        );
    }

    @AfterClass
    public static void cleanUp() {
        for (AdsConnector connector : connectors) {
            userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        }
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
    }
}
