package ru.yandex.autotests.metrika.tests.ft.management.goals.conditions.url;

import org.apache.commons.lang3.ArrayUtils;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.GoalObjectWrapper;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.steps.management.GoalsSteps.MAX_CONDITION_LEN;
import static ru.yandex.autotests.metrika.steps.management.GoalsSteps.MAX_CONDITION_REGEXP_COMPLEXITY;
import static ru.yandex.autotests.metrika.steps.management.GoalsSteps.MAX_CONTAIN_CONDITION_LEN;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getURLGoal;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.goals.GoalConditionType.*;

/**
 * Created by hamilkar on 10/13/16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Лимиты на длину урла в условии цели")
@Issue("METR-23014")
@RunWith(Parameterized.class)
public class UrlLengthLimitTest {

    private static UserSteps user;
    private static Long counterId;

    @Parameterized.Parameter(0)
    public GoalObjectWrapper goalWrapper;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                goalParams(getURLGoal(CONTAIN, MAX_CONTAIN_CONDITION_LEN)),
                goalParams(getURLGoal(REGEXP, MAX_CONDITION_REGEXP_COMPLEXITY-2)),
                goalParams(getURLGoal(EXACT, MAX_CONDITION_LEN)),
                goalParams(getURLGoal(START, MAX_CONDITION_LEN)),
                goalParams(getURLGoal(ACTION, MAX_CONDITION_LEN)),
                goalParams(getURLGoal(CONTAIN, 1)),
                goalParams(getURLGoal(REGEXP, 1)),
                goalParams(getURLGoal(EXACT, 1)),
                goalParams(getURLGoal(START, 1)),
                goalParams(getURLGoal(ACTION, 1))
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
        GoalE addedGoal = user.onManagementSteps().onGoalsSteps().addGoal(counterId, goalWrapper.getGoal());
        assertThat("добавленная цель должна быть эквивалентна добавляемой", addedGoal, beanEquivalent(goalWrapper.getGoal()));
    }

    private static Object[] goalParams(GoalE goal) {
        return ArrayUtils.toArray(new GoalObjectWrapper(goal));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
