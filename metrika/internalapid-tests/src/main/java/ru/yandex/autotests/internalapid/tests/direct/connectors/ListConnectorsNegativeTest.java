package ru.yandex.autotests.internalapid.tests.direct.connectors;

import java.util.ArrayList;
import java.util.List;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.tests.InternalApidTest;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.autotests.metrika.commons.response.CustomError;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;

@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Получение активных подключений по uid для платформы (негативные)")
public class ListConnectorsNegativeTest extends InternalApidTest {

    private static CounterFull counter;
    private static List<AdsConnector> connectors = new ArrayList<>();

    @BeforeClass
    public static void init() {
        counter = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
        connectors.add(userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId()));
        connectors.add(userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId()));
        connectors.add(userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId()));
    }

    @Test
    public void testFailToListNotExistingPlatform() {
        String platform = "not_existing_platform";
        userSteps.onDirectAdsConnectorsSteps().listConnectorsAndExpectError(
                platform,
                new CustomError(400L, allOf(containsString(platform), containsString("is not valid advertising " +
                        "platform")))
        );
    }

    @AfterClass
    public static void cleanUp() {
        for (AdsConnector connector : connectors) {
            userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(),
                    connector.getConnectorId());
        }
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
    }
}
