package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.junit.*;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Удаление подключения")
public class DeleteConnectorTest {

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);

    private CounterFull counter;
    private CounterFull counter2;
    private AdsConnector connector;

    @Before
    public void init() {
        counter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        counter2 = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        connector = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectSuccess(counter2.getId(), connector);
    }

    @Test
    public void testDeleteConnectorFromAllCounters() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());

        assertThat(
                "Удаляем подключение " + connector.getName() + " у счетчика " + counter.getId(),
                userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter.getId(), "", ""),
                emptyIterable()
        );

        assertThat(
                "Подключение полностью не удаленно, т.к. есть другой счетчик, использующий это подключение",
                userSteps.onManagementSteps().onAdsConnectorsSteps().listConnectorsAndExpectSuccess("google"),
                allOf(
                        iterableWithSize(greaterThanOrEqualTo(1)),
                        hasItem(beanEquivalent(connector))
                )
        );

        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter2.getId(), connector.getConnectorId());

        assertThat(
                "Удаляем подключение " + connector.getName() + " у счетчика " + counter2.getId(),
                userSteps.onManagementSteps().onAdsConnectorsSteps().getConnectorsByCounterAndExpectSuccess(counter2.getId(), "", ""),
                emptyIterable()
        );

        assertThat(
                "Подключение полностью удаленно",
                userSteps.onManagementSteps().onAdsConnectorsSteps().listConnectorsAndExpectSuccess("google"),
                not(hasItem(beanEquivalent(connector)))
        );
    }

    @After
    public void cleanUp() {
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter2.getId());
    }
}
