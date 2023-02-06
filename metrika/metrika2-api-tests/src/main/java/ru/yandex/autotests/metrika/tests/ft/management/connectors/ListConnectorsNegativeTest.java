package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.CustomError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Получение активных подключений по uid для платформы (негативные)")
public class ListConnectorsNegativeTest {

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
    public void testFailToListNotExistingPlatform() {
        String platform = "not_existing_platform";
        userSteps.onManagementSteps().onAdsConnectorsSteps().listConnectorsAndExpectError(
                platform,
                new CustomError(400L, allOf(containsString(platform), containsString("is not valid advertising platform")))
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
