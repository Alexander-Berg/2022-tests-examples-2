package ru.yandex.autotests.internalapid.tests.direct.connectors;

import java.util.ArrayList;
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
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.not;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;


@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Получение активных подключений для счетчика")
public class GetConnectorsForCounterTest  extends InternalApidTest {
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
    public void testGetAllConnectors() {
        assertThat(
                "Получаем все активные подключения для счетчика " + counter.getId(),
                userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "", ""),
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(connectors.size())),
                        hasItems(beanEquivalent(connectors.get(0)), beanEquivalent(connectors.get(1)), beanEquivalent(connectors.get(2)))
                )
        );
    }

    @Test
    public void testGetConnectorsByFilter() {
        String filter = connectors.get(0).getName().split("_")[1];
        assertThat(
                "Получаем подключения для счетчика " + counter.getId() + " по фильтру " + filter,
                userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "", filter),
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        hasItem(beanEquivalent(connectors.get(0)))
                )
        );
    }

    @Test
    public void testGetConnectorsByPlatformGoogle() {
        assertThat(
                "Получаем подключения для счетчика " + counter.getId() + " по платформе GOOGLE",
                userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "google", ""),
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(connectors.size())),
                        hasItems(beanEquivalent(connectors.get(0)), beanEquivalent(connectors.get(1)), beanEquivalent(connectors.get(2)))
                )
        );
    }

    @Test
    public void testGetConnectorsByPlatformFacebook() {
        assertThat(
                "Получаем подключения для счетчика " + counter.getId() + " по платформе Facebook",
                userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "facebook", ""),
                not(hasItems(beanEquivalent(connectors.get(0)), beanEquivalent(connectors.get(1)), beanEquivalent(connectors.get(2))))
        );
    }

    @AfterClass
    public static void cleanUp() {
        for (AdsConnector connector : connectors) {
            userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        }
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
    }
}
