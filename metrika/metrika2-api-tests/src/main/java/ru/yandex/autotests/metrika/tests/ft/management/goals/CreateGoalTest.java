package ru.yandex.autotests.metrika.tests.ft.management.goals;

import java.util.Arrays;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.*;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getEmailGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getFormGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getPhoneGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getStepGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getURLGoal;

/**
 * Created by konkov on 20.03.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Создание цели")
public class CreateGoalTest {

    private static UserSteps user;
    private static Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    @Issue("METRIKASUPP-4708")
    public void checkStepsGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(counterId, getStepGoal());
    }

    @Test
    public void checkPhoneGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(counterId, getPhoneGoal()
                .withConditions(Arrays.asList(getGoalCondition(GoalConditionType.EXACT, "+12345678")))
        );
        user.onManagementSteps().onGoalsSteps().addGoal(counterId, getPhoneGoal());
    }

    @Test
    public void checkEmailGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(counterId, getEmailGoal()
                .withConditions(Arrays.asList(getGoalCondition(GoalConditionType.EXACT, "asd@ru"))));
    }

    @Test
    public void checkFormGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(counterId, getFormGoal()
                .withConditions(Arrays.asList(getGoalCondition(GoalConditionType.FORM_ID, "asd"))));
    }

    // При создании цели через API => источник цели всегда должен быть равным к 'user'.
    // Если юзер кинет другой источник, например 'auto' => то как итог, во время десериализации из JSON в объект, источник должен приравняться к 'user'.
    @Issue("METR-42144")
    @Test
    public void tryToCreateGoalWithGoalSourceAuto() {
        GoalE goal = user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getURLGoal().withGoalSource(GoalSource.AUTO)
        );

        assertThat(goal.getGoalSource(), equalTo(GoalSource.USER));
    }

    @Test
    public void createGoalWithGoalSourceUser() {
        GoalE goal = user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getURLGoal().withGoalSource(GoalSource.USER)
        );

        assertThat(goal.getGoalSource(), equalTo(GoalSource.USER));
    }

    private GoalCondition getGoalCondition(GoalConditionType type, String url) {
        return new GoalCondition().withType(type).withUrl(url);
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
