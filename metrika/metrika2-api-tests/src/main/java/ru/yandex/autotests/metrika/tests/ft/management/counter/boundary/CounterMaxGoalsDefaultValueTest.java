package ru.yandex.autotests.metrika.tests.ft.management.counter.boundary;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.GOALS_LIMIT;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

/**
 * Created by konkov on 06.04.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Тест ограничения на количество целей в счетчике по умолчанию")
public class CounterMaxGoalsDefaultValueTest {

    private static final User USER = SIMPLE_USER;
    private static final int DEFAULT_MAX_GOALS = 200;

    private static UserSteps user;
    private Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(USER);
    }

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        user.onManagementSteps().onGoalsSteps().addGoals(counterId, getGoals(DEFAULT_MAX_GOALS));
    }

    @Test
    public void createMoreThanMaximumNumberOfGoals() {
        user.onManagementSteps().onGoalsSteps()
                .addGoalAndExpectError(GOALS_LIMIT, counterId, getGoal());
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
