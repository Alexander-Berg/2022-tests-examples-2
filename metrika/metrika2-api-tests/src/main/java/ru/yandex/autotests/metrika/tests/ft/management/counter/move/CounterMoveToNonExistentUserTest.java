package ru.yandex.autotests.metrika.tests.ft.management.counter.move;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.WRONG_LOGIN;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

/**
 * Created by konkov on 24.06.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка переноса счетчика, неcуществующий пользователь")
@Issue("METR-16688")
public class CounterMoveToNonExistentUserTest {

    private UserSteps user;

    private static final User OWNER = SIMPLE_USER;
    private static final User RECIPIENT = Users.NONEXISTENT_USER;

    private Long counterId;

    @Before
    public void before() {
        user = new UserSteps().withUser(OWNER);

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void negativeMoveTest() {
        user.onManagementSteps().onCountersSteps()
                .moveCounterAndExpectError(WRONG_LOGIN, counterId, RECIPIENT.get(LOGIN));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
