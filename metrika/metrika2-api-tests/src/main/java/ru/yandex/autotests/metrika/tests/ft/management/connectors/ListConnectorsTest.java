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
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.connectors.AdsPlatform.FACEBOOK;
import static ru.yandex.metrika.api.management.client.connectors.AdsPlatform.GOOGLE;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Получение активных подключений по uid для платформы")
public class ListConnectorsTest {

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);
    private static final UserSteps stranger = new UserSteps().withUser(SIMPLE_USER2);

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
    public void testListExistingGoogleConnections() {
        assertThat(
                "Получаем список активных подключений к Google Ads",
                userSteps.onManagementSteps().onAdsConnectorsSteps().listConnectorsAndExpectSuccess(GOOGLE.name()),
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(3)),
                        hasItems(beanEquivalent(connectors.get(0)), beanEquivalent(connectors.get(1)), beanEquivalent(connectors.get(2)))
                )
        );
    }

    @Test
    public void testListEmptyFacebookConnections() {
        assertThat(
                "Получаем пустой список подключений к Facebook",
                userSteps.onManagementSteps().onAdsConnectorsSteps().listConnectorsAndExpectSuccess(FACEBOOK.name()),
                iterableWithSize(0)
        );
    }

    @Test
    public void testStrangerCannotListConnectors() {
        assertThat(
                "Чужие подключения не возвращаються",
                stranger.onManagementSteps().onAdsConnectorsSteps().listConnectorsAndExpectSuccess(GOOGLE.name()),
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
