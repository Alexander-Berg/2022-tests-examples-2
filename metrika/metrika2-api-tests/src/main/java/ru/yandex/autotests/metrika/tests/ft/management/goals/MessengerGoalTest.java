package ru.yandex.autotests.metrika.tests.ft.management.goals;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collections;

import static ru.yandex.autotests.metrika.errors.ManagementError.INVALID_MESSENGER_GOAL_CONDITIONS;
import static ru.yandex.autotests.metrika.errors.ManagementError.INVALID_MESSENGER_GOAL_WITH_NO_CONDITIONS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getMessengerGoal;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Цель по переходам в мессенджеры")
public class MessengerGoalTest {
    private UserSteps user;
    private Long counterId;

    @Before
    public void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void createMessengerGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getMessengerGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.MESSENGER, "whatsapp")
                        )
                )
        );
    }

    @Test
    public void tryToCreateMessengerGoalWithManyGoalConditions() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_MESSENGER_GOAL_CONDITIONS,
                counterId,
                getMessengerGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.MESSENGER, "whatsapp"),
                                getGoalCondition(GoalConditionType.MESSENGER, "telegram")
                        )
                )
        );
    }

    @Test
    public void tryToCreateMessengerGoalWithNoGoalCondition() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_MESSENGER_GOAL_WITH_NO_CONDITIONS,
                counterId,
                getMessengerGoal().withConditions(
                        Collections.emptyList()
                )
        );
    }

    @Test
    public void createMessengerGoalWithTypeAllMessengers() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getMessengerGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.MESSENGER, "all_messengers")
                        )
                )
        );
    }

    @Test
    public void tryToCreateMessengerGoalWithTypeAllMessengersAndAlsoWithOneMoreAdditionalMessenger() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_MESSENGER_GOAL_CONDITIONS,
                counterId,
                getMessengerGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.MESSENGER, "all_messengers"),
                                getGoalCondition(GoalConditionType.MESSENGER, "viber")
                        )
                )
        );
    }

    private GoalCondition getGoalCondition(GoalConditionType type, String url) {
        return new GoalCondition().withType(type).withUrl(url);
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
