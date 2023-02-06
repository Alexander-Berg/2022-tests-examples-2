package ru.yandex.autotests.internalapid.tests.direct.connectors;

import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.tests.InternalApidTest;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.internalapid.tests.direct.connectors.AdsConnectorsTestUtils.buildDefaultCabinet;
import static ru.yandex.autotests.internalapid.tests.direct.connectors.AdsConnectorsTestUtils.deepCopyConnector;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Изменения подключения")
public class UpdateConnectorTest  extends InternalApidTest {
    private static CounterFull counter;

    private AdsConnector connector;

    @BeforeClass
    public static void init() {
        counter = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
    }

    @Before
    public void setUp() {
        // создаём коннектор
        connector = userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        // добавляем кабинет
        connector = connector.withCabinets(Collections.singletonList(buildDefaultCabinet()));
        // обновляем коннектор для сохранения кабинета
        connector = userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), connector);
    }

    @Test
    public void testUpdateName() {
        AdsConnector update = deepCopyConnector(connector).withName("test_ads_connector_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date()));

        assertThat(
                "Изменить имя подключения " + connector.getName(),
                userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
                beanEquivalent(connector).withVariation(
                        new DefaultMatchVariation()
                                .forFields("name")
                                .useMatcher(equalTo(update.getName()))
                )
        );
    }

    @Test
    public void testUpdateCabinetsAdd() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(Collections.singletonList(buildDefaultCabinet().withCustomerAccountId(1L)));

        assertThat(
                "Добавить кабинет к подключению " + connector.getName(),
                userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
                beanEquivalent(connector).withVariation(
                        new DefaultMatchVariation()
                                .forFields("cabinets")
                                .useMatcher(beanEquivalent(update.getCabinets()))
                )
        );
    }

    @Test
    public void testUpdateCabinetsDelete() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(null);

        assertThat(
                "Удалить кабинет из подключения " + connector.getName(),
                userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
                beanEquivalent(connector).withVariation(
                        new DefaultMatchVariation()
                                .forFields("cabinets")
                                .useMatcher(iterableWithSize(0))
                )
        );
    }

    @Test
    public void testUpdateCabinetsUndelete() {

        AdsConnector update = deepCopyConnector(connector);
        // удаляем существующий кабинет
        update = userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update.withCabinets(null));

        update = update.withCabinets(Collections.singletonList(buildDefaultCabinet().withCustomerAccountId(1L)));

        assertThat(
                "Разделить кабинет у подключения " + connector.getName(),
                userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
                beanEquivalent(connector).withVariation(
                        new DefaultMatchVariation()
                                .forFields("cabinets")
                                .useMatcher(beanEquivalent(update.getCabinets()))
                )
        );
    }

    @Test
    public void testUpdateCabinetsChangeName() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(Collections.singletonList(buildDefaultCabinet().withCustomerAccountName("updated_" + System.currentTimeMillis())));

        assertThat(
                "Изменить имя у кабинета подключения " + connector.getName(),
                userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
                beanEquivalent(connector).withVariation(
                        new DefaultMatchVariation()
                                .forFields("cabinets")
                                .useMatcher(beanEquivalent(update.getCabinets()))
                )
        );
    }

    @After
    public void shutdown() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
    }
}
