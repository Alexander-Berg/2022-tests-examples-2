package ru.yandex.autotests.metrika.tests.ft.management.counter.permission;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.COUNTERS, Requirements.Story.Management.PERMISSION})
public class CounterPermissionPinTest {
    private static final User OWNER = Users.SIMPLE_USER7;
    private static final User SUPPORT = Users.USER_WITH_PIN_SUPPORT_ROLE;
    private static final User CLIENT = Users.USER_FOR_PIN_ACCESS_TEST;
    private static final User OTHER = Users.USER_DELEGATOR5;

    private static UserSteps owner;
    private static UserSteps client;
    private static UserSteps support;
    private static UserSteps other;

    private static CounterFull counter;

    @BeforeClass
    public static void setup() {
        owner = new UserSteps().withUser(OWNER);
        client = new UserSteps().withUser(CLIENT);
        support = new UserSteps().withUser(SUPPORT);
        other = new UserSteps().withUser(OTHER);
        counter = owner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        owner.onManagementSteps().onDelegatesSteps()
                .addDelegateAndExpectSuccess(new DelegateE().withUserLogin(CLIENT.get(LOGIN)), ignoreQuota(true));
        client.onManagementSteps().onDelegatesSteps()
                .addDelegateAndExpectSuccess(new DelegateE().withUserLogin(SUPPORT.get(LOGIN)), ignoreQuota(true));
        client.onManagementSteps().onDelegatesSteps()
                .addDelegateAndExpectSuccess(new DelegateE().withUserLogin(OTHER.get(LOGIN)), ignoreQuota(true));
    }

    @Test
    @Title("Проверка доступа к счетчику транзитивно через представителей при наличии соотв. роли.")
    public void testCounterAccess() {
        support.onManagementSteps().onCountersSteps().getCounterInfo(counter.getId());

        support.onManagementSteps().onCountersSteps().editCounter(counter.getId(), getDefaultCounter());
    }

    @Test
    @Title("Проверка отсутствия транзитивного доступа при отсутствии соотв. роли")
    public void testCounterAccessNegative() {
        other.onManagementSteps().onCountersSteps().getCounterInfoAndExpectError(ACCESS_DENIED, counter.getId());
    }

    @AfterClass
    public static void cleanup() {
        owner.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(CLIENT.get(LOGIN));
        client.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(SUPPORT.get(LOGIN));
        client.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(OTHER.get(LOGIN));
        owner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
    }
}
