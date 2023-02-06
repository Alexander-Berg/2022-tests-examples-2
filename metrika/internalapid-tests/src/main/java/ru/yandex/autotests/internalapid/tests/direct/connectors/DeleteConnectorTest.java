package ru.yandex.autotests.internalapid.tests.direct.connectors;

import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.internalapid.tests.InternalApidTest;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.emptyIterable;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.not;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;


@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Удаление подключения")
public class DeleteConnectorTest extends InternalApidTest {

    private CounterFull counter;
    private CounterFull counter2;
    private AdsConnector connector;

    @Before
    public void init() {
        counter = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
        counter2 = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test2.ru"));
        connector = userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectSuccess(counter2.getId(), connector);
    }

    @Test
    public void testDeleteConnectorFromAllCounters() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());

        assertThat(
                "Удаляем подключение " + connector.getName() + " у счетчика " + counter.getId(),
                userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "", ""),
                not(hasItem(beanEquivalent(connector)))
        );

        assertThat(
                "Подключение полностью не удаленно, т.к. есть другой счетчик, использующий это подключение",
                userSteps.onDirectAdsConnectorsSteps().listConnectorsAndExpectSuccess("google"),
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        hasItem(beanEquivalent(connector))
                )
        );

        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter2.getId(), connector.getConnectorId());

        assertThat(
                "Удаляем подключение " + connector.getName() + " у счетчика " + counter2.getId(),
                userSteps.onDirectAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter2.getId(), "", ""),
                not(Matchers.contains(connector))
        );

        assertThat(
                "Подключение полностью удаленно",
                userSteps.onDirectAdsConnectorsSteps().listConnectorsAndExpectSuccess("google"),
                not(hasItem(beanEquivalent(connector)))
        );
    }

    @After
    public void cleanUp() {
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
        userSteps.onInternalApidSteps().deleteCounter(counter2.getId());
    }
}
