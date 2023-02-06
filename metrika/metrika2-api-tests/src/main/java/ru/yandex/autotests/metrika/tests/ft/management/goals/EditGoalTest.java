package ru.yandex.autotests.metrika.tests.ft.management.goals;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getUrlGoalWithConditions;

/**
 * Created by konkov on 25.09.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Редактирование цели")
public class EditGoalTest {

    private static UserSteps user;
    private static Long counterId;

    private Long goalId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Before
    public void setup() {
        goalId = user.onManagementSteps().onGoalsSteps().addGoal(counterId, getUrlGoalWithConditions(1)).getId();
    }

    @Test
    @Issue("METR-18165")
    public void checkEditGoal() {
        user.onManagementSteps().onGoalsSteps().editGoal(counterId, goalId, getUrlGoalWithConditions(2));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

}
