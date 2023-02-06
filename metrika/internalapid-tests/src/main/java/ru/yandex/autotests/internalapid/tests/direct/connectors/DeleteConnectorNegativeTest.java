package ru.yandex.autotests.internalapid.tests.direct.connectors;

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

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.internalapid.matchers.CommonError.NOT_FOUND;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;

@Features("API управления")
@Stories("Подключения рекламных кабинетов")
@Title("Удаление подключения (негативные)")
public class DeleteConnectorNegativeTest extends InternalApidTest {

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
    public void testFailToDeleteRandomConnector() {
        userSteps.onDirectAdsConnectorsStepsSimpleUser().deleteConnectorAndExpectError(
                counter.getId(),
                connector.getConnectorId(),
                new CustomError(403L, containsString("Access is denied"))
        );
    }

    @Test
    public void testFailToDeleteInexistingConnector() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectError(counter.getId(), 1L, NOT_FOUND);
    }

    @AfterClass
    public static void cleanUp() {
        userSteps.onDirectAdsConnectorsSteps().deleteConnectorAndExpectSuccess(counter.getId(), connector.getConnectorId());
        userSteps.onInternalApidSteps().deleteCounter(counter.getId());
    }
}
