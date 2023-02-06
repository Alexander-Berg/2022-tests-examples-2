package ru.yandex.autotests.metrika.tests.ft.management.goals.conditions.boundary;

import org.junit.After;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

/**
 * Created by konkov on 06.04.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Создание цели с условиями, тест не стандартных ограничений")
public class CreateGoalWithConditionsCustomLimitTest {

    private static final User USER = SIMPLE_USER;
    private static final Counter COUNTER = Counters.TEST_CONDITIONS_LIMIT;
    private static final int MAX_CONDITIONS = 100;

    private static UserSteps user;

    private Long addedGoalId;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(USER);
    }

    @Test
    public void createGoalWithMaximumConditions() {
        addedGoalId = user.onManagementSteps().onGoalsSteps()
                .addGoal(COUNTER.get(ID), getUrlGoalWithoutConditions().withConditions(getConditions(MAX_CONDITIONS)))
                .getId();
    }

    @Test
    public void createGoalWithMoreThanMaximumConditions() {
        user.onManagementSteps().onGoalsSteps()
                .addGoalAndExpectError(CONDITIONS_LIMIT, COUNTER.get(ID),
                        getUrlGoalWithConditions(MAX_CONDITIONS + 1));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onGoalsSteps().deleteGoal(COUNTER.get(ID), addedGoalId);
    }
}
