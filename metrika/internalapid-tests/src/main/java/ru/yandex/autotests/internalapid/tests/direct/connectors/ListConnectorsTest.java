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
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.metrika.api.management.client.connectors.AdsPlatform.FACEBOOK;
import static ru.yandex.metrika.api.management.client.connectors.AdsPlatform.GOOGLE;

@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Получение активных подключений по uid для платформы")
public class ListConnectorsTest  extends InternalApidTest {

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
    public void testListExistingGoogleConnections() {
        assertThat(
                "Получаем список активных подключений к Google Ads",
                userSteps.onDirectAdsConnectorsSteps().listConnectorsAndExpectSuccess(GOOGLE.name()),
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
                userSteps.onDirectAdsConnectorsSteps().listConnectorsAndExpectSuccess(FACEBOOK.name()),
                iterableWithSize(0)
        );
    }

    @Test
    public void testStrangerCannotListConnectors() {
        assertThat(
                "Чужие подключения не возвращаються",
                userSteps.onDirectAdsConnectorsStepsSimpleUser().listConnectorsAndExpectSuccess(GOOGLE.name()),
                iterableWithSize(0)
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
