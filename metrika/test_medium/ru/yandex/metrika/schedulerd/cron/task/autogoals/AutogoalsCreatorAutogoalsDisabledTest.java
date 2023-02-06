package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.ArrayList;
import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.autogoals.AutoGoals;

/**
 * не должны создаваться автоцели, если autogoals_enabled = 0 у счетчика
 * (кроме ecom целей, но они не должны быть видны пользователю)
 */
@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractAutogoalsCreatorTest.AutogoalsConfig.class})
public class AutogoalsCreatorAutogoalsDisabledTest extends AbstractAutogoalsCreatorTest {

    @Parameterized.Parameter
    public AutogoalCandidateInfoBrief input;

    @Parameterized.Parameter(1)
    public String testName;

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {

        //common autogoals test
        var result = new ArrayList<Object[]>();
        for (int i = 0; i < limit; i++) {
            result.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithDisabledAutogoals(),
                            new int[]{i},
                            new String[]{}
                    ), "AutogoalsCreator test for autogoals_enabled=0, type = " + AutoGoals.Type.forNumber(i)
            });
        }
        //partners autogoals test
        for (var partnersGoalAction : allPartnerAutogoalsToTest) {
            result.add(new Object[]{
                    new AutogoalCandidateInfoBrief(
                            getCounterIdWithDisabledAutogoals(),
                            new int[]{AutoGoals.Type.PARTNER_VALUE},
                            new String[]{partnersGoalAction}
                    ), "AutogoalsCreator test for partners goals with autogoals_enabled=0, type = " + partnersGoalAction
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

        var goals = goalsService.getGoalsWithNames(input.getCounterId());
        Assert.assertEquals(0, goals.size());
    }
}
