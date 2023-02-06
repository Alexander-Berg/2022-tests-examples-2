package ru.yandex.autotests.internalapid.tests.direct.connectors;

import java.util.List;

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

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;


@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Создание подключений")
public class AddConnectorTest extends InternalApidTest {
    private static long counterId;
    private static long otherCounterId;

    private static AdsConnector connector;
    private static AdsConnector dubbedConnector;

    @BeforeClass
    public static void init() {
        counterId = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru")).getId();
        otherCounterId = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test2.ru")).getId();

        connector = userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counterId);
        dubbedConnector = userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectSuccess(otherCounterId, connector);
    }

    @Test
    public void testAddNewConnector() {
        List<AdsConnector> connectors = userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counterId, "", "");
        assertThat(
                "новое подключение успешно созданно",
                connectors,
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        hasItem(beanEquivalent(connector))
                )
        );
    }

    @Test
    public void testAddExistingConnectorToCounter() {
        List<AdsConnector> connectors = userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(otherCounterId, "", "");
        assertThat(
                "существующее подключение успешно добавленно к счетчику " + otherCounterId,
                connectors,
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        hasItem(beanEquivalent(dubbedConnector))
                )
        );
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(otherCounterId, dubbedConnector.getConnectorId());
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counterId, connector.getConnectorId());

        userSteps.onInternalApidSteps().deleteCounter(counterId);
        userSteps.onInternalApidSteps().deleteCounter(otherCounterId);
    }
}
