package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.management.client.external.goals.ActionGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.metrika.autogoals.AutoGoals;
import ru.yandex.metrika.util.StringUtil;

import static org.junit.Assert.assertEquals;

/**
 * если изменить partners_goals.action, необходимо изменить ad_goals_urls.url
 *
 * создадим на счетчике цели, потом переименуем partners_goals.action и снова попробуем создать цели на счетчике
 * все поля ad_goals_urls должны остаться без изменений, кроме url - он должен принять новое значение
 */
@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractAutogoalsCreatorTest.AutogoalsConfig.class})
public class AutogoalsCreatorPartnersGoalsRenameActionTest extends AbstractAutogoalsCreatorTest {
    @Parameterized.Parameter
    public AutogoalCandidateInfoBrief preinput;

    @Parameterized.Parameter(1)
    public String testName;

    @Parameterized.Parameter(2)
    public AutogoalCandidateInfoBrief renamedInput;

    private String originalPartnerGoalAction;
    private String renamedPartnerGoalAction;

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<Object[]>();

        for (var partnersGoalAction : allPartnerAutogoalsToTest) {
            result.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{AutoGoals.Type.PARTNER_VALUE},
                            new String[]{partnersGoalAction}),
                    "AutogoalsCreator test with rename action in partners_goals, input url = " + partnersGoalAction,
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{AutoGoals.Type.PARTNER_VALUE},
                            new String[]{partnersGoalAction.replaceFirst("Jivo_|ym-", "")})
            });
        }
        return result;
    }

    @Before
    public void pre() {
        cleanAllGoals(preinput.getCounterId());
        autogoalsCreator.checkAndCreateOrUpdate(List.of(preinput));
        originalPartnerGoalAction = partnersGoalsRegexpActionsMap.getOrDefault(preinput.getActions()[0], preinput.getActions()[0]);
        renamedPartnerGoalAction = originalPartnerGoalAction.replaceFirst("Jivo_|ym-|ym\\\\-", "");
        renameActionInDatabase(originalPartnerGoalAction, renamedPartnerGoalAction);
    }

    @After
    public void after() {
        renameActionInDatabase(renamedPartnerGoalAction, originalPartnerGoalAction);
    }

    private void renameActionInDatabase(String oldAction, String newAction) {
        countersTemplate.update(
                "UPDATE partners_goals SET action = " + StringUtil.escape(newAction) +
                        " WHERE action = " + StringUtil.escape(oldAction));
        partnersGoalsDao.reload();
    }

    @Test
    public void test() {
        //сначала проверяем что предсоздана цель до переименования
        var goals = goalsService.findByCounterId(preinput.getCounterId(), false);
        checkInputPartnersAutogoalsEquality(goals, List.of(preinput.getActions()), partnersGoalsRegexpActionsMap);

        //пробуем создать новую партнёрскую автоцель
        autogoalsCreator.checkAndCreateOrUpdate(List.of(renamedInput));

        //проверяем что цель переименовалась
        goals = goalsService.findByCounterId(renamedInput.getCounterId(), false);
        checkInputPartnersAutogoalsEquality(goals, List.of(renamedInput.getActions()), renamedPartnersGoalsRegexpActionsMap);
    }

    private void checkInputPartnersAutogoalsEquality(List<GoalE> goals,
                                                     List<String> expectedPartnersGoalsActions,
                                                     Map<String, String> regexpActionsMap) {
        assertEquals(expectedPartnersGoalsActions.size(), goals.size());
        assertEquals(goals.size(), 1);
        assertEquals(goals.get(0).getType(), GoalType.action);
        String actionName = expectedPartnersGoalsActions.get(0);
        GoalCondition condition = ((ActionGoal) goals.get(0)).getConditions().get(0);
        if (regexpActionsMap.containsKey(actionName)) {
            Assert.assertEquals(GoalConditionType.regexp, condition.getOperator());
            Assert.assertEquals(regexpActionsMap.get(actionName), condition.getValue());
        } else {
            Assert.assertEquals(GoalConditionType.exact, condition.getOperator());
            Assert.assertEquals(actionName, condition.getValue());
        }
    }
}
