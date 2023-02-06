package ru.yandex.autotests.metrika.tests.ft.management.goals;

import java.util.Collection;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getActionGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getEmailGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getNumberGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getPhoneGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getURLGoal;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;


@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Цели со стоимостью по умолчанию")
@Issue("METR-37088")
@RunWith(Parameterized.class)
public class GoalsWithDefaultPrice {
    private static UserSteps user = new UserSteps();
    private static long counterId;
    private Long goalId;
    private double defaultPrice = 199.99;

    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public GoalE goal;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][] {
                {"Простая цель", getGoal()},
                {"JavaScript-событие.", getActionGoal()},
                {"Нажатие на email.", getEmailGoal()},
                {"Количество просмотров.", getNumberGoal()},
                {"Нажатие на номер телефона.", getPhoneGoal()},
                {"Посещение страниц.", getURLGoal()},
        });
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Before
    public void setup() {
        goalId = user.onManagementSteps().onGoalsSteps().addGoal(counterId, goal).getId();
    }

    @Test
    public void checkEditGoal() {
        GoalE result =  user
                .onManagementSteps()
                .onGoalsSteps()
                .editGoal(counterId, goalId, goal.withDefaultPrice(this.defaultPrice));
        assertThat(
                "цель изменила стоимость по умолчанию",
                result,
                beanEquivalent(
                        goal.withDefaultPrice(this.defaultPrice)
                )
        );
    }


    @Test
    public void checkCreateGoal() {
        GoalE result =  user
                .onManagementSteps()
                .onGoalsSteps()
                .addGoal(
                        counterId,
                        goal.withDefaultPrice(this.defaultPrice)
                );
        assertThat(
                "цель создана стоимость по умолчанию",
                result,
                beanEquivalent(
                        goal.withDefaultPrice(this.defaultPrice)
                )
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
