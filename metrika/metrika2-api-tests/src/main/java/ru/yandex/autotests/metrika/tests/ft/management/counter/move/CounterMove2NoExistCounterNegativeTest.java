package ru.yandex.autotests.metrika.tests.ft.management.counter.move;

import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.metrika.errors.ManagementError.COUNTER_DOESNT_EXIST;

/**
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка отбирания счетчика, негативнные тесты")
public class CounterMove2NoExistCounterNegativeTest {

    private static final User OWNER = USER_DELEGATOR;
    private static UserSteps userOwner = new UserSteps().withUser(OWNER);

    @Test
    public void negativeMoveTest() {
        userOwner.onManagementSteps().onCountersSteps()
                .move2CounterAndExpectError(COUNTER_DOESNT_EXIST, -1L, "test", SIMPLE_USER2.get(LOGIN));
    }

}
