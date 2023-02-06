package ru.yandex.autotests.metrika.tests.ft.management.goals;

import java.util.Collection;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionOperator;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.call.CallGoalField;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.GOALS)
@Title("Создание цели (негативные)")
@RunWith(Parameterized.class)
public class CreateGoalNegativeTest {

    private static UserSteps user = new UserSteps();
    private static long counterId;

    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public GoalE goal;

    @Parameterized.Parameter(2)
    public IExpectedError expectedError;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][] {
                { "цель без имени", getGoalWithoutName(), EMPTY_GOAL_NAME },
                { "цель с пустым именем", getGoalWithEmptyName(), EMPTY_GOAL_NAME },
                { "цель с emoji в имени", getURLGoal().withName("\uD83D\uDCC5"), NOT_ALLOWED_SYMBOLS_IN_GOAL_NAME },
                { "составная цель с шагом без имени", getCompositeGoalWithStepWithoutName(), EMPTY_GOAL_NAME },
                { "составная цель с шагом с пустым именем", getCompositeGoalWithStepWithEmptyName(), EMPTY_GOAL_NAME },
                { "url цель без условий", getUrlGoalWithoutConditions(), EMPTY_GOAL_CONDITION },
                { "url цель с недопустимыми символами", getURLGoal(GoalConditionType.CONTAIN, "\uD83D\uDCC5"), NOT_ALLOWED_SYMBOLS_IN_CONDITION_VALUE },
                { "email цель c action условием", getEmailGoalWithActionCondition(), NOT_VALID_GOAL_CONDITION },
                { "url цель c form_xpath условием", getUrlGoallWithFormXpathCondition(), NOT_VALID_GOAL_CONDITION },
                { "messenger цель с неправильным condition type", getMessengerGoalWithWrongConditionType(), NOT_VALID_GOAL_CONDITION},
                { "messenger цель с неправильным condition value", getMessengerGoalWithWrongConditionValue(), INVALID_GOAL_CONDITION},
                { "цель \"Скачивание файлов\" с неправильным condition type", getFileGoalWithWrongConditionType(), NOT_VALID_GOAL_CONDITION},
                { "цель \"Звонок\", условие \"Длительность звонка\" без оператора", getConditionalCallGoalCallDurationWithoutOperator(), CONDITION_TYPE_DOES_NOT_SPECIFIED},
                { "цель \"Звонок\", условие \"Метка\" с недопустимыми символами", getConditionalCallGoal(CallGoalField.CALL_TAG, GoalConditionOperator.EXACT, "\uD83D\uDCC5"), NOT_ALLOWED_SYMBOLS_IN_CONDITION_VALUE},
                { "цель \"Звонок\", условие \"Метка\" с невалидным значением", getConditionalCallGoalCallTagWithInvalidValue(), SIZE_MUST_BE_BETWEEN},
                { "social network цель с неправильным condition type", getSocialNetworkGoalWithWrongConditionType(), NOT_VALID_GOAL_CONDITION},
                { "social network цель с неправильным condition value", getSocialNetworkGoalWithWrongConditionValue(), INVALID_GOAL_CONDITION},
                { "цель URL с неправильными condition type contain_action", getUrlGoalWithContainActionConditions(), NOT_VALID_GOAL_CONDITION},
                { "цель URL с неправильными condition type regexp_action", getUrlGoalWithRegexpActionConditions(), NOT_VALID_GOAL_CONDITION}
        });
    }

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void test() {
        user.onManagementSteps().onGoalsSteps()
                .addGoalAndExpectError(expectedError, counterId, goal);
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
