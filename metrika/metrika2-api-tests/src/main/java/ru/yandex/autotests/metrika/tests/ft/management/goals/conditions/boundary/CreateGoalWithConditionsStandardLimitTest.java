package ru.yandex.autotests.metrika.tests.ft.management.goals.conditions.boundary;

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
import static ru.yandex.autotests.metrika.errors.ManagementError.CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getUrlGoalWithConditions;

/**
 * Created by konkov on 06.04.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Создание цели с условиями, тест стандартных ограничений")
public class CreateGoalWithConditionsStandardLimitTest {

    private static final User USER = SIMPLE_USER;
    private static final int MAX_CONDITIONS = 10;

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
    }

    @Test
    public void createGoalWithMaximumConditions() {
        user.onManagementSteps().onGoalsSteps()
                .addGoal(counterId, getUrlGoalWithConditions(MAX_CONDITIONS));
    }

    @Test
    public void createGoalWithMoreThanMaximumConditions() {
        user.onManagementSteps().onGoalsSteps()
                .addGoalAndExpectError(CONDITIONS_LIMIT, counterId,
                        getUrlGoalWithConditions(MAX_CONDITIONS + 1));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
