package ru.yandex.autotests.internalapid.tests.direct.connectors;

import java.util.Collections;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.tests.InternalApidTest;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.autotests.metrika.commons.response.CustomError;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.lang.String.valueOf;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.internalapid.matchers.CommonError.MAY_NOT_BE_NULL;
import static ru.yandex.autotests.internalapid.matchers.CommonError.MUST_BE_GREATER_THAN_OR_EQUAL_TO;
import static ru.yandex.autotests.internalapid.matchers.CommonError.NOT_FOUND;
import static ru.yandex.autotests.internalapid.tests.direct.connectors.AdsConnectorsTestUtils.buildDefaultCabinet;
import static ru.yandex.autotests.internalapid.tests.direct.connectors.AdsConnectorsTestUtils.buildDefaultConnector;

@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Создание подключений (негативный)")
public class AddConnectorNegativeTest extends InternalApidTest {

    private static CounterFull counter;
    private static CounterFull otherCounter;

    private AdsConnector orig;

    @BeforeClass
    public static void init() {
        counter = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
        otherCounter = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test2.ru"));
    }

    @Before
    public void setup() {
        orig = userSteps.onDirectAdsConnectorsSteps().createConnectorWithoutAuthorizationAndExpectSuccess(counter.getId());
        orig = userSteps.onDirectAdsConnectorsSteps()
                .updateConnectorAndExpectSuccess(counter.getId(), orig.getConnectorId(), orig.withCabinets(Collections.singletonList(buildDefaultCabinet())));
    }

    @Test
    public void testFailToAddConnectorTwice() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                counter.getId(),
                orig,
                new CustomError(400L, allOf(containsString(valueOf(counter.getId())), containsString(orig.getName()), containsString(orig.getPlatform().name())))
        );
    }

    @Test
    public void testFailToAddConnectorWithInvalidId() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withConnectorId(0L),
                MUST_BE_GREATER_THAN_OR_EQUAL_TO
        );
    }

    @Test
    public void testFailToAddConnectorWithNotExistingId() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withConnectorId(2147483647L),
                NOT_FOUND
        );
    }

    @Test
    public void testFailToAddConnectorWithoutName() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withName(null),
                MAY_NOT_BE_NULL
        );
    }

    @Test
    public void testFailToAddCabinetWithInvalidId() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountId(0L)).collect(toList())),
                MUST_BE_GREATER_THAN_OR_EQUAL_TO
        );
    }

    @Test
    public void testFailToAddCabinetWithoutName() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountName(null)).collect(toList())),
                MAY_NOT_BE_NULL
        );
    }

    @Test
    public void testFailToAddCabinetWithoutTimezone() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountTimezone(null)).collect(toList())),
                MAY_NOT_BE_NULL
        );
    }

    @Test
    public void testFailToAddCabinetWithoutCurrency() {
        userSteps.onDirectAdsConnectorsSteps().createConnectorAndExpectError(
                otherCounter.getId(),
                buildDefaultConnector(orig.getConnectorId(), orig.getPlatform()).withCabinets(orig.getCabinets().stream().peek(c -> c.setCustomerAccountCurrency(null)).collect(toList())),
                MAY_NOT_BE_NULL
        );
    }

    @After
    public void shutdown() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), orig.getConnectorId());
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
        userSteps.onInternalApidSteps().deleteCounter(otherCounter.getId());
    }
}
