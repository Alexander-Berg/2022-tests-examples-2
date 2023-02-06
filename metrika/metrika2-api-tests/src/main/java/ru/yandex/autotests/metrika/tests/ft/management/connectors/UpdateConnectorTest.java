package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.junit.*;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsCabinet;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.connectors.AdsConnectorsTestUtils.buildDefaultCabinet;
import static ru.yandex.autotests.metrika.tests.ft.management.connectors.AdsConnectorsTestUtils.deepCopyConnector;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Изменения подключения")
public class UpdateConnectorTest {

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);

    private static CounterFull counter;

    private AdsConnector connector;

    @BeforeClass
    public static void init() {
        counter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
    }

    @Before
    public void setUp() {
        // создаём коннектор
        connector = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        // добавляем кабинет
        connector = connector.withCabinets(Collections.singletonList(buildDefaultCabinet()));
        // обновляем коннектор для сохранения кабинета
        connector = userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), connector);
    }

    @Test
    public void testUpdateName() {
        AdsConnector update = deepCopyConnector(connector).withName("test_ads_connector_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date()));

        assertThat(
                "Изменить имя подключения " + connector.getName(),
                userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
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
                userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
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
                userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
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
        update = userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update.withCabinets(null));

        update = update.withCabinets(Collections.singletonList(buildDefaultCabinet().withCustomerAccountId(1L)));

        assertThat(
                "Разделить кабинет у подключения " + connector.getName(),
                userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
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
                userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId(), update),
                beanEquivalent(connector).withVariation(
                        new DefaultMatchVariation()
                                .forFields("cabinets")
                                .useMatcher(beanEquivalent(update.getCabinets()))
                )
        );
    }

    @After
    public void shutdown() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
    }
}
