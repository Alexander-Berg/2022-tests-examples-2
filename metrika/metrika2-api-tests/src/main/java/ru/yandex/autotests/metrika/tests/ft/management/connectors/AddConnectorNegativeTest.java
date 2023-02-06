package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import org.junit.*;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.CustomError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collections;

import static java.lang.String.valueOf;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.CommonError.MAY_NOT_BE_NULL;
import static ru.yandex.autotests.metrika.errors.CommonError.MUST_BE_GREATER_THAN_OR_EQUAL_TO;
import static ru.yandex.autotests.metrika.errors.ManagementError.NOT_FOUND;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.connectors.AdsConnectorsTestUtils.buildDefaultCabinet;
import static ru.yandex.autotests.metrika.tests.ft.management.connectors.AdsConnectorsTestUtils.buildDefaultConnector;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.ADS_CONNECTORS)
@Title("Создание подключений (негативный)")
public class AddConnectorNegativeTest {

    private static final UserSteps userSteps = new UserSteps().withUser(SIMPLE_USER);

    private static CounterFull counter;
    private static CounterFull otherCounter;

    private AdsConnector orig;

    @BeforeClass
    public static void init() {
        counter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        otherCounter = userSteps.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
    }

    @Before
    public void setup() {
        orig = userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        orig = userSteps.onManagementSteps()
                .onAdsConnectorsSteps()
                .updateConnectorAndExpectSuccess(counter.getId(), orig.getConnectorId(), orig.withCabinets(Collections.singletonList(buildDefaultCabinet())));
    }

    @Test
    public void testFailToAddConnectorTwice() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                counter.getId(),
                orig,
                new CustomError(400L, allOf(containsString(valueOf(counter.getId())), containsString(orig.getName()), containsString(orig.getPlatform().name())))
        );
    }

    @Test
    public void testFailToAddConnectorWithInvalidId() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withConnectorId(0L),
                MUST_BE_GREATER_THAN_OR_EQUAL_TO
        );
    }

    @Test
    public void testFailToAddConnectorWithNotExistingId() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withConnectorId(2147483647L),
                NOT_FOUND
        );
    }

    @Test
    public void testFailToAddConnectorWithoutName() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withName(null),
                MAY_NOT_BE_NULL
        );
    }

    @Test
    public void testFailToAddCabinetWithInvalidId() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountId(0L)).collect(toList())),
                MUST_BE_GREATER_THAN_OR_EQUAL_TO
        );
    }

    @Test
    public void testFailToAddCabinetWithoutName() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountName(null)).collect(toList())),
                MAY_NOT_BE_NULL
        );
    }

    @Test
    public void testFailToAddCabinetWithoutTimezone() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountTimezone(null)).collect(toList())),
                MAY_NOT_BE_NULL
        );
    }

    @Test
    public void testFailToAddCabinetWithoutCurrency() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountCurrency(null)).collect(toList())),
                MAY_NOT_BE_NULL
        );
    }

    @After
    public void shutdown() {
        userSteps.onManagementSteps().onAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), orig.getConnectorId());
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
        userSteps.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(otherCounter.getId());
    }
}
