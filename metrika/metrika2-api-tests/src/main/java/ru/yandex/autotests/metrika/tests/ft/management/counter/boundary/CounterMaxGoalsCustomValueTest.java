package ru.yandex.autotests.metrika.tests.ft.management.counter.boundary;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_COUNTER_LIMITS;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.GOALS;
import static ru.yandex.autotests.metrika.errors.ManagementError.GOALS_LIMIT;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGoals;

/**
 * Created by konkov on 06.04.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Тест заданного ограничения на количество целей в счетчике")
public class CounterMaxGoalsCustomValueTest {

    private static final User USER = SIMPLE_USER;
    private static final Counter COUNTER = TEST_COUNTER_LIMITS;
    private static final int CUSTOM_MAX_GOALS = 210;

    private static UserSteps user;

    private List<GoalE> addedGoals = new ArrayList<>();

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(USER);
    }

    @Before
    public void setup() {
        CounterFull counterInfo = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(COUNTER.get(ID), GOALS);

        int currentUserGoals = (int) counterInfo.getGoals()
                .stream()
                .filter(x -> x.getGoalSource() != GoalSource.AUTO).count();

        List<GoalE> goals = getGoals(CUSTOM_MAX_GOALS - currentUserGoals);

        addedGoals = user.onManagementSteps().onGoalsSteps().addGoals(COUNTER.get(ID), goals);
    }

    @Test
    public void createMoreThanMaximumNumberOfGoals() {
        user.onManagementSteps().onGoalsSteps()
                .addGoalAndExpectError(GOALS_LIMIT, COUNTER.get(ID), getGoal());
    }

    @After
    public void teardown() {
        user.onManagementSteps().onGoalsSteps().deleteGoals(COUNTER.get(ID), addedGoals);
    }

}
