package ru.yandex.metrika.schedulerd.cron.task.autogoals;

import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalSource;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.metrika.autogoals.AutoGoals;

import static org.apache.commons.lang3.ArrayUtils.toArray;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractAutogoalsCreatorTest.AutogoalsConfig.class})
public class AutogoalsCreatorACartAPurchaseTest extends AbstractAutogoalsCreatorTest {

    private List<GoalE> existingGoals;

    @Parameterized.Parameter
    public String msg;

    @Parameterized.Parameter(1)
    public int counterId;

    @Parameterized.Parameter(2)
    public GoalType type;

    @Parameterized.Parameter(3)
    public boolean expectCreation;

    @Parameterized.Parameters(name = "{2}: {0}")
    public static List<Object[]> getParameters() {
        return List.of(
                toArray("no existing goals", 44, GoalType.a_cart, true),
                toArray("active call goal exists", 45, GoalType.a_cart, true),
                toArray("active e_cart goal exists", 46, GoalType.a_cart, false),
                toArray("deleted e_cart goal exists", 47, GoalType.a_cart, false),
                toArray("active a_cart goal exists", 48, GoalType.a_cart, false),
                toArray("deleted a_cart goal exists", 49, GoalType.a_cart, false),
                toArray("active a_purchase goal exists", 50, GoalType.a_cart, true),
                toArray("deleted a_purchase goal exists", 51, GoalType.a_cart, true),
                toArray("active e_cart and deleted a_purchase goals exist", 52, GoalType.a_cart, false),
                toArray("active e_cart and active a_purchase goals exist", 53, GoalType.a_cart, false),
                toArray("deleted e_cart and deleted a_purchase goals exist", 54, GoalType.a_cart, false),
                toArray("hidden e_cart goal exists", 66, GoalType.a_cart, false),

                toArray("no existing goals", 55, GoalType.a_purchase, true),
                toArray("active call goal exists", 56, GoalType.a_purchase, true),
                toArray("active e_cart goal exists", 57, GoalType.a_purchase, false),
                toArray("deleted e_cart goal exists", 58, GoalType.a_purchase, false),
                toArray("active a_cart goal exists", 59, GoalType.a_purchase, true),
                toArray("deleted a_cart goal exists", 60, GoalType.a_purchase, true),
                toArray("active a_purchase goal exists", 61, GoalType.a_purchase, false),
                toArray("deleted a_purchase goal exists", 62, GoalType.a_purchase, false),
                toArray("active e_cart and deleted a_purchase goals exist", 63, GoalType.a_purchase, false),
                toArray("active e_cart and active a_purchase goals exist", 64, GoalType.a_purchase, false),
                toArray("deleted e_cart and deleted a_purchase goals exist", 65, GoalType.a_purchase, false),
                toArray("hidden e_cart goal exists", 67, GoalType.a_purchase, false)
        );
    }

    @Before
    public void setUp() {
        existingGoals = goalsService.findByCounterId(counterId, true);
        autogoalsCreator.checkAndCreateOrUpdate(
                List.of(
                        new AutogoalCandidateInfoBrief(
                                counterId,
                                new int[]{convert(type).getNumber()},
                                null
                        )
                )
        );
    }

    @Test
    public void test() {
        List<GoalE> goals = goalsService.findByCounterId(counterId, true);

        long newACartGoalsCount = goals.stream()
                .filter(g -> g.getType() == type && g.getGoalSource() == GoalSource.auto)
                .count();
        long existingACartGoalsCount = existingGoals.stream()
                .filter(g -> g.getType() == type && g.getGoalSource() == GoalSource.auto)
                .count();

        Assert.assertEquals(
                "a_cart goal is " + (expectCreation ? "not " : "") + "created",
                expectCreation ? 1 : 0,
                newACartGoalsCount - existingACartGoalsCount
        );
    }

    private static AutoGoals.Type convert(GoalType type) {
        return switch (type) {
            case a_cart -> AutoGoals.Type.A_CART;
            case a_purchase -> AutoGoals.Type.A_PURCHASE;
            default -> throw new IllegalArgumentException(type + " is incorrect type");
        };
    }
}
