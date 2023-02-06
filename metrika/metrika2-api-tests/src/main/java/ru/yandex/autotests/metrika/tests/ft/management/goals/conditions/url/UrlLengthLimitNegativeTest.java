package ru.yandex.autotests.metrika.tests.ft.management.goals.conditions.url;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.GoalObjectWrapper;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.errors.ManagementError.CAN_NOT_BE_EMPTY_CONDITION_URL;
import static ru.yandex.autotests.metrika.errors.ManagementError.CONDITION_URL_LENGTH_LIMIT;
import static ru.yandex.autotests.metrika.errors.ManagementError.INVALID_GOAL_CONDITION;
import static ru.yandex.autotests.metrika.steps.management.GoalsSteps.MAX_CONDITION_LEN;
import static ru.yandex.autotests.metrika.steps.management.GoalsSteps.MAX_CONDITION_REGEXP_COMPLEXITY;
import static ru.yandex.autotests.metrika.steps.management.GoalsSteps.MAX_CONTAIN_CONDITION_LEN;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getFileGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getSiteSearchGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getURLGoal;
import static ru.yandex.metrika.api.management.client.external.goals.GoalConditionType.*;

/**
 * Created by hamilkar on 10/13/16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Лимиты на длину урла в условии цели (негативные)")
@Issue("METR-23014")
@RunWith(Parameterized.class)
public class UrlLengthLimitNegativeTest {

    private static UserSteps user;
    private static Long counterId;

    @Parameterized.Parameter(0)
    public GoalObjectWrapper goalWrapper;

    @Parameterized.Parameter(1)
    public ManagementError error;


    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>of(
                goalParams(getURLGoal(CONTAIN, MAX_CONTAIN_CONDITION_LEN + 1), CONDITION_URL_LENGTH_LIMIT),
                goalParams(getURLGoal(REGEXP, MAX_CONDITION_REGEXP_COMPLEXITY - 1), INVALID_GOAL_CONDITION),
                goalParams(getURLGoal(EXACT, MAX_CONDITION_LEN + 1), CONDITION_URL_LENGTH_LIMIT),
                goalParams(getURLGoal(START, MAX_CONDITION_LEN + 1), CONDITION_URL_LENGTH_LIMIT),
                goalParams(getURLGoal(ACTION, MAX_CONDITION_LEN + 1), CONDITION_URL_LENGTH_LIMIT),
                goalParams(getURLGoal(REGEXP, "*abc*"), INVALID_GOAL_CONDITION),
                goalParams(getURLGoal(CONTAIN, ""), CAN_NOT_BE_EMPTY_CONDITION_URL),
                goalParams(getURLGoal(REGEXP, ""), CAN_NOT_BE_EMPTY_CONDITION_URL),
                goalParams(getURLGoal(EXACT, ""), CAN_NOT_BE_EMPTY_CONDITION_URL),
                goalParams(getURLGoal(START, ""), CAN_NOT_BE_EMPTY_CONDITION_URL),
                goalParams(getURLGoal(ACTION, ""), CAN_NOT_BE_EMPTY_CONDITION_URL),
                goalParams(getFileGoal(MAX_CONDITION_LEN + 1), CONDITION_URL_LENGTH_LIMIT),
                goalParams(getSiteSearchGoal(MAX_CONDITION_LEN + 1), CONDITION_URL_LENGTH_LIMIT)
        );
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void checkGoalWithCondition() {
        user.onManagementSteps().onGoalsSteps().addGoalAndExpectError(error, counterId, goalWrapper.getGoal());
    }

    private static Object[] goalParams(GoalE goal, ManagementError error) {
        return ArrayUtils.toArray(new GoalObjectWrapper(goal), error);
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
