package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.management.client.external.goals.ActionGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.metrika.autogoals.AutoGoals;

/**
 * При создании партнёрских целей мы проверяем не наличие целей такого же типа (ActionGoal),
 * а наличие целей такого же типа с таким же url'ом в условиях и pattern_type'ом exact/regexp
 *
 * Поэтому насоздаем на счётчике action автоцелей с разными url'ами, а потом попробуем добавить новый
 */
@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractAutogoalsCreatorTest.AutogoalsConfig.class})
public class AutogoalsCreatorPartnersGoalsWithPrecreatedManyButTheOneTest extends AbstractAutogoalsCreatorTest {
    @Parameterized.Parameter
    public AutogoalCandidateInfoBrief input;

    @Parameterized.Parameter(1)
    public String testName;

    @Parameterized.Parameter(2)
    public AutogoalCandidateInfoBrief preinput;

    @Parameterized.Parameter(3)
    public boolean deletePrecreatedGoal;

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<Object[]>();

        Set.of(true, false).forEach(dPG -> {
            for (var partnersGoalAction : allPartnerAutogoalsToTest) {
                var tmpPreinputActionTypes = new ArrayList<>(allPartnerAutogoalsToTest);
                tmpPreinputActionTypes.remove(partnersGoalAction);
                result.add(new Object[]{
                        new AutogoalCandidateInfoBrief(
                                getCounterIdWithEnabledAutogoals(),
                                new int[]{AutoGoals.Type.PARTNER_VALUE},
                                new String[]{partnersGoalAction}
                        ), "AutogoalsCreator test with precreated" +
                        (dPG ? " and deleted" : "") +
                        " all other partners auto goals, testing action type = " + partnersGoalAction,
                        new AutogoalCandidateInfoBrief(
                                getCounterIdWithEnabledAutogoals(),
                                new int[]{AutoGoals.Type.PARTNER_VALUE},
                                tmpPreinputActionTypes.toArray(new String[0])
                        ),
                        dPG,
                });
            }
        });
        return result;
    }

    @Before
    public void pre() {
        cleanAllGoals(preinput.getCounterId());
        autogoalsCreator.checkAndCreateOrUpdate(List.of(preinput));
        if (deletePrecreatedGoal) {
            markAllGoalsAsDeleted(preinput.getCounterId());
        }
    }

    @Test
    public void test() {
        //сначала проверяем что предсозданы все остальные типы партнёрских автоцелей
        var goals = goalsService.findByCounterId(input.getCounterId(), true);
        checkPartnersAutogoalsEquality(goals, List.of(preinput.getActions()));

        //создаём новую партнёрскую автоцель
        autogoalsCreator.checkAndCreateOrUpdate(List.of(input));

        //проверяем что есть все типы партнёрских целей
        goals = goalsService.findByCounterId(input.getCounterId(), true);
        checkPartnersAutogoalsEquality(goals, allPartnerAutogoalsToTest);
    }

    void checkPartnersAutogoalsEquality(List<GoalE> goals, List<String> expectedPartnersGoalsActions) {
        //проверяем количество
        Assert.assertEquals(expectedPartnersGoalsActions.size(), goals.size());
        var partnersGoalsTypesPreCreated = goals.stream()
                .filter(goal -> goal.getType() == GoalType.action)
                .map(goal -> ((ActionGoal) goal).getConditions().get(0).getValue())
                .collect(Collectors.toSet());
        //проверяем, что это те самые
        expectedPartnersGoalsActions.forEach(expected ->
            partnersGoalsTypesPreCreated.remove(partnersGoalsRegexpActionsMap.getOrDefault(expected, expected)));
        Assert.assertEquals(0, partnersGoalsTypesPreCreated.size());
    }
}
