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

import static ru.yandex.autotests.metrika.errors.ManagementError.CAN_NOT_BE_EMPTY_CONDITION_URL;
import static ru.yandex.autotests.metrika.errors.ManagementError.INVALID_BUTTON_GOAL_WITH_NO_CONDITIONS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getButtonGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Цель клик по кнопке")
public class ButtonGoalTest {
    private UserSteps user;
    private Long counterId;

    @Before
    public void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void createButtonGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getButtonGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.BTN_TYPE, "url_1"),
                                getGoalCondition(GoalConditionType.BTN_CONTENT, "url_2")
                        )
                )
        );
    }

    @Test
    public void tryToCreateButtonGoalWithNoGoalCondition() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_BUTTON_GOAL_WITH_NO_CONDITIONS,
                counterId,
                getButtonGoal().withConditions(
                        Collections.emptyList()
                )
        );
    }

    @Test
    public void tryToCreateButtonGoalsWithEmptyConditionUrl() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                CAN_NOT_BE_EMPTY_CONDITION_URL,
                counterId,
                getButtonGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.BTN_TYPE, ""),
                                getGoalCondition(GoalConditionType.BTN_CONTENT, null)
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
