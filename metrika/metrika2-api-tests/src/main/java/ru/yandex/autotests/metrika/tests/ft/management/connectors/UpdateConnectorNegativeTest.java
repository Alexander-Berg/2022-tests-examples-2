package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.hamcrest.Matchers;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.errors.CustomError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.lang.String.valueOf;
import static java.util.Collections.singletonList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.errors.CommonError.MAY_NOT_BE_NULL;
import static ru.yandex.autotests.metrika.errors.CommonError.SIZE_MUST_BE_BETWEEN;
import static ru.yandex.autotests.metrika.errors.ReportError.MUST_BE_GREATER_THAN_OR_EQUAL_TO_1;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.connectors.AdsConnectorsTestUtils.buildDefaultCabinet;
import static ru.yandex.autotests.metrika.tests.ft.management.connectors.AdsConnectorsTestUtils.deepCopyConnector;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Изменения подключения (негативные)")
public class UpdateConnectorNegativeTest {

    private static User GUEST = SIMPLE_USER2;

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);
    private static final UserSteps stranger = new UserSteps().withUser(GUEST);

    private static CounterFull counter;
    private static AdsConnector connector;

    @BeforeClass
    public static void init() {
        counter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        connector = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        userSteps.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(
                counter.getId(),
                new GrantE()
                        .withUserLogin(GUEST.get(LOGIN))
                        .withPerm(EDIT)
        );
    }

    @Test
    public void testFailToDeleteName() {
        AdsConnector update = deepCopyConnector(connector).withName(null);
        userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(counter.getId(), connector.getConnectorId(), update, MAY_NOT_BE_NULL);
    }

    @Test
    public void testFailToSetEmptyName() {
        AdsConnector update = deepCopyConnector(connector).withName("");
        userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(counter.getId(), connector.getConnectorId(), update, SIZE_MUST_BE_BETWEEN);
    }

    @Test
    public void testFailToChangeConnectorId() {
        AdsConnector update = deepCopyConnector(connector).withConnectorId(10L);
        userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                new CustomError(400L, Matchers.equalTo("Ambiguous connector IDs"))
        );
    }

    @Test
    public void testFailToChangeRandomConnector() {
        AdsConnector update = deepCopyConnector(connector);
        stranger.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                new CustomError(403L, allOf(containsString("does not own"), containsString(valueOf(connector.getConnectorId()))))
        );
    }

    @Test
    public void testFailToSetInvalidCabinetName() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountName("")));
        userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                SIZE_MUST_BE_BETWEEN
        );
    }

    @Test
    public void testFailToSetInvalidCabinetTimezone() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountTimezone("")));
        userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                SIZE_MUST_BE_BETWEEN
        );
    }

    @Test
    public void testFailToSetInvalidCabinetCurrency() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountCurrency("")));
        userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                SIZE_MUST_BE_BETWEEN
        );
    }

    @Test
    public void testFailToSetInvalidCabinetId() {
        AdsConnector update = deepCopyConnector(connector).withCabinets(singletonList(buildDefaultCabinet().withCustomerAccountId(0L)));
        userSteps.onManagementSteps().onAdsConnectorsSteps().updateConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                update,
                MUST_BE_GREATER_THAN_OR_EQUAL_TO_1
        );
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
    }
}
