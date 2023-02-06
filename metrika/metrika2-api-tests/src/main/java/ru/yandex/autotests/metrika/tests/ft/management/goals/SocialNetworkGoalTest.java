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

import static ru.yandex.autotests.metrika.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Цель по переходам в социальные сети")
public class SocialNetworkGoalTest {
    private UserSteps user;
    private Long counterId;

    @Before
    public void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void createSocialNetworkGoal() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getSocialNetworkGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.SOCIAL, "vkontakte")
                        )
                )
        );
    }

    @Test
    public void tryToCreateSocialNetworkGoalWithManyGoalConditions() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_SOCIAL_NETWORK_GOAL_CONDITIONS,
                counterId,
                getSocialNetworkGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.SOCIAL, "vkontakte"),
                                getGoalCondition(GoalConditionType.SOCIAL, "twitter")
                        )
                )
        );
    }

    @Test
    public void tryToCreateSocialNetworkGoalWithNoGoalCondition() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_SOCIAL_NETWORK_GOAL_WITH_NO_CONDITIONS,
                counterId,
                getSocialNetworkGoal().withConditions(
                        Collections.emptyList()
                )
        );
    }

    @Test
    public void createSocialNetworkGoalWithConditionTypeAllSocial() {
        user.onManagementSteps().onGoalsSteps().addGoal(
                counterId,
                getSocialNetworkGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.ALL_SOCIAL, "")
                        )
                )
        );
    }

    @Test
    public void tryToCreateSocialNetworkGoalWithConditionTypeAllSocialAndAlsoWithOneMoreAdditionalSocialNetwork() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(
                INVALID_SOCIAL_NETWORK_GOAL_CONDITIONS,
                counterId,
                getSocialNetworkGoal().withConditions(
                        Arrays.asList(
                                getGoalCondition(GoalConditionType.ALL_SOCIAL, ""),
                                getGoalCondition(GoalConditionType.SOCIAL, "vkontakte")
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

