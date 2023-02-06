package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.ArrayList;
import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.management.client.external.goals.ActionGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.metrika.autogoals.AutoGoals;

/**
 * проверяем создание автоцелей в простейшем случае:
 * autogoals_enabled = 1, других целей на счетчике нет
 */
@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractAutogoalsCreatorTest.AutogoalsConfig.class})
public class AutogoalsCreatorSimpleTest extends AbstractAutogoalsCreatorTest {
    @Parameterized.Parameter
    public AutogoalCandidateInfoBrief input;

    @Parameterized.Parameter(1)
    public String testName;

    @Parameterized.Parameter(2)
    public boolean isPartnerGoal;

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {

        var result = new ArrayList<Object[]>();
        //common autogoals test
        for (int i = 0; i < limit; i++) {
            if (getIgnoredTypes().contains(i)) {
                continue;
            }
            result.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{i},
                            new String[]{}
                    ), "AutogoalsCreator simple creation test, type = " + AutoGoals.Type.forNumber(i),
                    false
            });
        }
        //partners autogoals test
        for (var partnersGoalAction : allPartnerAutogoalsToTest) {
            result.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{AutoGoals.Type.PARTNER_VALUE},
                            new String[]{partnersGoalAction}
                    ), "AutogoalsCreator partners goal simple creation test, type = " + partnersGoalAction,
                    true
            });
        }
        return result;
    }

    @Before
    public void pre() {
        cleanAllGoals(input.getCounterId());
    }

    @Test
    public void test() {
        autogoalsCreator.checkAndCreateOrUpdate(List.of(input));

        var goals = goalsService
                .findByCounterIds(List.of(input.getCounterId()), false, true, true)
                .getOrDefault(input.getCounterId(), List.of());
        Assert.assertEquals(1, goals.size());
        var goal = goals.get(0);
        if (isPartnerGoal) {
            checkPartnersGoal(input.getCounterId(), goal, input.getActions()[0]);
        } else {
            checkGoal(input.getCounterId(), goal,
                    autogoalsCreator.getGoalTypeFromCH(input.getAutogoalsTypesToCreate()[0]));
        }
    }

    void checkGoal(int counterId, GoalE goal, GoalType goalType) {
        Assert.assertEquals(counterId, goal.getCounterId());
        Assert.assertEquals(GoalSource.auto, goal.getGoalSource());
        Assert.assertEquals(goalType, goal.getType());
    }

    void checkPartnersGoal(int counterId, GoalE goal, String actionName) {
        checkGoal(counterId, goal, GoalType.action);

        Assert.assertEquals(1, ((ActionGoal) goal).getConditions().size());

        var condition = ((ActionGoal) goal).getConditions().get(0);
        if (partnersGoalsRegexpActionsMap.containsKey(actionName)) {
            Assert.assertEquals(GoalConditionType.regexp, condition.getOperator());
            Assert.assertEquals(partnersGoalsRegexpActionsMap.get(actionName), condition.getValue());
        } else {
            Assert.assertEquals(GoalConditionType.exact, condition.getOperator());
            Assert.assertEquals(actionName, condition.getValue());
        }
    }
}
