package ru.yandex.autotests.internalapid.tests.direct.connectors;

import org.hamcrest.Matchers;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.beans.data.Users;
import ru.yandex.autotests.internalapid.tests.InternalApidTest;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.autotests.metrika.commons.response.CustomError;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.internalapid.matchers.CommonError.MAY_NOT_BE_NULL;
import static ru.yandex.autotests.internalapid.matchers.CommonError.MUST_BE_GREATER_THAN_OR_EQUAL_TO_1;
import static ru.yandex.autotests.internalapid.matchers.CommonError.SIZE_MUST_BE_BETWEEN;
import static ru.yandex.autotests.internalapid.tests.direct.connectors.AdsConnectorsTestUtils.buildDefaultCabinet;
import static ru.yandex.autotests.internalapid.tests.direct.connectors.AdsConnectorsTestUtils.deepCopyConnector;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;

@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Изменения подключения (негативные)")
public class UpdateConnectorNegativeTest extends InternalApidTest {

    private static CounterFull counter;
    private static AdsConnector connector;

    @BeforeClass
    public static void init() {
        counter = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
        connector = userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        userSteps.onInternalApidSteps().addGrant(
                counter.getId(),
                new GrantE()
                        .withUserLogin(Users.SIMPLE_USER2.get(User.LOGIN))
                        .withPerm(EDIT)
        );
    }

    @Test
    public void testFailToDeleteName() {
        AdsConnector update = deepCopyConnector(connector).withName(null);
        userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectError(counter.getId(), connector.getConnectorId(), update, MAY_NOT_BE_NULL);
    }

    @Test
    public void testFailToSetEmptyName() {
        AdsConnector update = deepCopyConnector(connector).withName("");
        userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectError(counter.getId(), connector.getConnectorId(), update, SIZE_MUST_BE_BETWEEN);
    }

    @Test
    public void testFailToChangeConnectorId() {
        AdsConnector update = deepCopyConnector(connector).withConnectorId(10L);
        userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                new CustomError(400L, Matchers.equalTo("Ambiguous connector IDs"))
        );
    }

    @Test
    public void testFailToChangeRandomConnector() {
        AdsConnector update = deepCopyConnector(connector);
        userSteps.onDirectAdsConnectorsStepsSimpleUser().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                new CustomError(403L, containsString("Access is denied"))
        );
    }

    @Test
    public void testFailToSetInvalidCabinetName() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountName("")));
        userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                SIZE_MUST_BE_BETWEEN
        );
    }

    @Test
    public void testFailToSetInvalidCabinetTimezone() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountTimezone("")));
        userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                SIZE_MUST_BE_BETWEEN
        );
    }

    @Test
    public void testFailToSetInvalidCabinetCurrency() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountCurrency("")));
        userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                SIZE_MUST_BE_BETWEEN
        );
    }

    @Test
    public void testFailToSetInvalidCabinetId() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountId(0L)));
        userSteps.onDirectAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                MUST_BE_GREATER_THAN_OR_EQUAL_TO_1
        );
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
    }
}
