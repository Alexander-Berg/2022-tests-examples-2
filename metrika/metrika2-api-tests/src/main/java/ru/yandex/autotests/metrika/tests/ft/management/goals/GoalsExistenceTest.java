package ru.yandex.autotests.metrika.tests.ft.management.goals;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.NO_QUOTA_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_FOR_CHECK_GOALS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGoal;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGrant;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Проверка наличия целей")
public class GoalsExistenceTest {

    private static UserSteps testUserSteps;
    private final static User testUser = USER_FOR_CHECK_GOALS;
    private static UserSteps granterUserSteps;
    private final static User granterUser = SIMPLE_USER;

    private Long firstTestCounter;
    private Long secondTestCounter;

    private Long delegatedCounterId;
    private Long delegatedGoalId;

    @BeforeClass
    public static void init() {
        testUserSteps = new UserSteps().withUser(testUser);
        testUserSteps.onManagementSteps().onCountersSteps().deleteAllCounters();
        granterUserSteps = new UserSteps().withUser(granterUser);
    }

    @Before
    public void setup() {
        firstTestCounter = testUserSteps.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        secondTestCounter = testUserSteps.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        delegatedCounterId = granterUserSteps.onManagementSteps()
                .onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        delegatedGoalId = granterUserSteps
                .onManagementSteps()
                .onGoalsSteps()
                .addGoal(delegatedCounterId, getGoal())
                .getId();
    }

    public void checkAbsenceOfGoals() {
        Long result = testUserSteps.onManagementSteps().onGoalsSteps().checkGoalsExistence().getValue();

        assertThat("Целей создано не было", result, beanEquivalent(0L));
    }

    public void checkGoalsExistence() {
        Long goalId = testUserSteps.onManagementSteps().onGoalsSteps().addGoal(firstTestCounter, getGoal()).getId();

        Long result = testUserSteps.onManagementSteps().onGoalsSteps().checkGoalsExistence().getValue();

        assertThat("Были созданы цели", result, beanEquivalent(1L));

        testUserSteps.onManagementSteps().onGoalsSteps().deleteGoal(firstTestCounter, goalId);
    }

    public void checkGrantedGoalsExistence() {
        granterUserSteps.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(
                delegatedCounterId,
                getGrant(testUser)
        );

        Long result = testUserSteps.onManagementSteps().onGoalsSteps().checkGoalsExistence().getValue();

        assertThat("Был дан доступ на редактирование к счетчику с созданной целью", result, beanEquivalent(1L));
    }

    public void checkGrantedGoalsAbsence() {
        Long result = testUserSteps.onManagementSteps().onGoalsSteps().checkGoalsExistence().getValue();

        assertThat("Был дан доступ на редактирование к счетчику с созданной целью", result, beanEquivalent(0L));
    }

    public void checkUserWithoutCounters() {
        Long result = new UserSteps().withUser(NO_QUOTA_USER).onManagementSteps().onGoalsSteps().checkGoalsExistence().getValue();
        assertThat("Вызов ручки отработал", result, beanEquivalent(0L));
    }

    @Test
    public void checkGoalsTests() {
        checkAbsenceOfGoals();
        checkGoalsExistence();
        checkGrantedGoalsAbsence();
        checkGrantedGoalsExistence();
        checkUserWithoutCounters();
    }

    @After
    public void cleanup() {
        testUserSteps.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(firstTestCounter);
        testUserSteps.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(secondTestCounter);

        granterUserSteps.onManagementSteps().onGoalsSteps().deleteGoal(delegatedCounterId, delegatedGoalId);
        granterUserSteps.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(delegatedCounterId);
    }
}
