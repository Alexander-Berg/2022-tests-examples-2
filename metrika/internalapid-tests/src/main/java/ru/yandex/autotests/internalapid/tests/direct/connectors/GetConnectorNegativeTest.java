package ru.yandex.autotests.internalapid.tests.direct.connectors;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.tests.InternalApidTest;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.internalapid.matchers.CommonError.NOT_FOUND;
import static ru.yandex.autotests.internalapid.matchers.CommonError.NO_OBJECT_ID;


@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Получение подключения (негативный)")
public class GetConnectorNegativeTest extends InternalApidTest {

    private static CounterFull counter;
    private static AdsConnector connector;

    @BeforeClass
    public static void init() {
        counter = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
        connector = userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
    }

    @Test
    public void testFailGetNotExistingConnector() {
        userSteps.onDirectAdsConnectorsSteps().getConnectorAndExpectError(counter.getId(), 0L, NO_OBJECT_ID);
    }

    @Test
    public void testFailGetConnectorForNotExistingId() {
        userSteps.onDirectAdsConnectorsSteps().getConnectorAndExpectError(0L, connector.getConnectorId(), NOT_FOUND);
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
    }
}
