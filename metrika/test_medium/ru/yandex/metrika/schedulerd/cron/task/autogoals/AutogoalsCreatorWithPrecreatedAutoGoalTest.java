package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.function.BiConsumer;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.metrika.autogoals.AutoGoals;

/**
 * Автоцели не должны создаваться, если уже есть автоцель такого же типа (удалённая или активная).
 * <p>
 * для партнёрских целей, всё то же самое, но на уровне url'а condition'а, а не на уровне типа цели
 */
@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractAutogoalsCreatorTest.AutogoalsConfig.class})
public class AutogoalsCreatorWithPrecreatedAutoGoalTest extends AbstractAutogoalsCreatorTest {

    @Parameterized.Parameter
    public AutogoalCandidateInfoBrief input;

    @Parameterized.Parameter(1)
    public String testName;

    @Parameterized.Parameter(2)
    public boolean deletePrecreatedGoal;

    static BiConsumer<Boolean, List<Object[]>> forCommonAutoGoals = (deletePrecreatedGoal, acc) -> {
        for (int i = 0; i < limit; i++) {
            if (getIgnoredTypes().contains(i)) {
                continue;
            }
            acc.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{i},
                            new String[]{}
                    ),
                    "AutogoalsCreator test with precreated" +
                            (deletePrecreatedGoal ? " and deleted" : "") +
                            " autogoal, type = " + AutoGoals.Type.forNumber(i),
                    deletePrecreatedGoal
            });
        }
    };

    static BiConsumer<Boolean, List<Object[]>> forPartnersAutoGoals = (deletePrecreatedGoal, acc) -> {
        for (var partnersGoalAction : allPartnerAutogoalsToTest) {
            acc.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithEnabledAutogoals(),
                            new int[]{AutoGoals.Type.PARTNER_VALUE},
                            new String[]{partnersGoalAction}
                    ), "AutogoalsCreator test with precreated" +
                    (deletePrecreatedGoal ? " and deleted" : "") +
                    " partners auto goal, action type = " + partnersGoalAction,
                    deletePrecreatedGoal,
            });
        }
    };

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        var result = new ArrayList<Object[]>();
        Set.of(true, false).forEach(dPG -> {
            forCommonAutoGoals.accept(dPG, result);
            forPartnersAutoGoals.accept(dPG, result);
        });
        return result;
    }

    @Before
    public void pre() {
        cleanAllGoals(input.getCounterId());
        autogoalsCreator.checkAndCreateOrUpdate(List.of(input));
        if (deletePrecreatedGoal) {
            markAllGoalsAsDeleted(input.getCounterId());
        }
    }

    @Test
    public void test() {
        autogoalsCreator.checkAndCreateOrUpdate(List.of(input));

        // Если deletePrecreatedGoal, то проверяем наличие одной удаленной автоцели,
        // иначе - наличие одной предсозданной автоцели
        // для партнёрских целей, всё то же самое, но на уровне url'а condition'а (то есть action'а цели), а не на уровне типа цели
        List<GoalE> goals;
        int counterId = input.getCounterId();
        if (deletePrecreatedGoal) {
            goals = goalsService
                    .findByCounterIds(List.of(counterId), false, true, true)
                    .getOrDefault(counterId, List.of());
            Assert.assertEquals(0, goals.size());
            goals = goalsService
                    .findByCounterIds(List.of(counterId), true, true, false)
                    .getOrDefault(counterId, List.of());
        } else {
            goals = goalsService
                    .findByCounterIds(List.of(counterId), false, true, true)
                    .getOrDefault(counterId, List.of());
        }
        Assert.assertEquals(1, goals.size());
        var goal = goals.get(0);
        Assert.assertEquals(input.getCounterId(), goal.getCounterId());
        Assert.assertEquals(GoalSource.auto, goal.getGoalSource());
        Assert.assertEquals(autogoalsCreator.getGoalTypeFromCH(input.getAutogoalsTypesToCreate()[0]), goal.getType());
    }
}
