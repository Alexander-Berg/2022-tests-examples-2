package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addJsonAttachment;

/**
 * Created by konkov on 20.03.2015.
 */
public class GoalsSteps extends MetrikaBaseSteps {

    public static final int MAX_CONTAIN_CONDITION_LEN = 1024;
    public static final int MAX_CONDITION_LEN = 16384;
    public static final int MAX_CONDITION_REGEXP_COMPLEXITY = 8192;

    @Step("Получить список целей для счетчика {0}")
    public List<GoalE> getGoals(Long counterId, boolean sorted, boolean deleted) {
        return getGoals(SUCCESS_MESSAGE, expectSuccess(), counterId, sorted, deleted).getGoals();
    }

    public List<GoalE> getGoals(Long counterId) {
        return getGoals(counterId, false, false);
    }

    @Step("Получить список целей для счетчика {1} и ожидать ошибку {0}")
    public List<GoalE> getGoalsAndExpectError(IExpectedError error, Long counterId) {
        return getGoals(ERROR_MESSAGE, expectError(error), counterId, false, false).getGoals();
    }

    private ManagementV1CounterCounterIdGoalsGETSchema getGoals(String message, Matcher matcher,
                                                                Long counterId, boolean sorted, boolean deleted) {
        ManagementV1CounterCounterIdGoalsGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/goals", counterId)).get())
                .readResponse(ManagementV1CounterCounterIdGoalsGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить информацию о цели {1} счетчика {0}")
    public GoalE getGoal(Long counterId, Long goalId) {
        return getGoal(SUCCESS_MESSAGE, expectSuccess(), counterId, goalId).getGoal();
    }

    @Step("Получить информацию о цели {2} счетчика {1} и ожидать ошибку {0}")
    public GoalE getGoalAndExpectError(IExpectedError error, Long counterId, Long goalId) {
        return getGoal(ERROR_MESSAGE, expectError(error), counterId, goalId).getGoal();
    }

    private ManagementV1CounterCounterIdGoalGoalIdGETSchema getGoal(String message, Matcher matcher,
                                                                    Long counterId, Long goalId) {
        ManagementV1CounterCounterIdGoalGoalIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/goal/%s", counterId, goalId)).get())
                .readResponse(ManagementV1CounterCounterIdGoalGoalIdGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать цели для счетчика {0}")
    public List<GoalE> addGoals(Long counterId, List<GoalE> goals) {
        addJsonAttachment(String.format("Всего целей %s", goals.size()), JsonUtils.toString(goals));

        return goals.stream().map(goal -> addGoal(counterId, goal)).collect(toList());
    }

    @Step("Создать цель для счетчика {0}")
    public GoalE addGoal(Long counterId, GoalE goal) {
        return addGoal(SUCCESS_MESSAGE, expectSuccess(), counterId, goal).getGoal();
    }

    @Step("Создать цель для счетчика {1} и ожидать ошибку {0}")
    public GoalE addGoalAndExpectError(IExpectedError error, Long counterId, GoalE goal) {
        return addGoal(ERROR_MESSAGE, expectError(error), counterId, goal).getGoal();
    }

    private ManagementV1CounterCounterIdGoalsPOSTSchema addGoal(String message, Matcher matcher,
                                                                Long counterId, GoalE goal) {
        ManagementV1CounterCounterIdGoalsPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/goals", counterId))
                        .post(new ManagementV1CounterCounterIdGoalsPOSTRequestSchema().withGoal(goal)))
                .readResponse(ManagementV1CounterCounterIdGoalsPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить цель {1} для счетчика {0}")
    public GoalE editGoal(Long counterId, Long goalId, GoalE goal) {
        return editGoal(SUCCESS_MESSAGE, expectSuccess(), counterId, goalId, goal).getGoal();
    }

    @Step("Изменить цель {2} для счетчика {1} и ожидать ошибку {0}")
    public GoalE editGoalAndExpectError(IExpectedError error, Long counterId, Long goalId, GoalE goal) {
        return editGoal(ERROR_MESSAGE, expectError(error), counterId, goalId, goal).getGoal();
    }

    private ManagementV1CounterCounterIdGoalGoalIdPUTSchema editGoal(String message, Matcher matcher,
                                                                     Long counterId, Long goalId, GoalE goal) {
        ManagementV1CounterCounterIdGoalGoalIdPUTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/goal/%s", counterId, goalId))
                        .put(new ManagementV1CounterCounterIdGoalGoalIdPUTRequestSchema().withGoal(goal)))
                .readResponse(ManagementV1CounterCounterIdGoalGoalIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить цели у счетчика {0}")
    public void deleteGoals(Long counterId, List<GoalE> goals) {
        addJsonAttachment(String.format("Всего целей %s", goals.size()), JsonUtils.toString(goals));

        goals.forEach(goal -> deleteGoal(counterId, goal.getId()));
    }

    @Step("Удалить цель {1} счетчика {0}")
    public void deleteGoal(Long counterId, Long goalId) {
        if (goalId != null) {
            deleteGoal(SUCCESS_MESSAGE, expectSuccess(), counterId, goalId);
        }
    }

    @Step("Удалить цель {2} счетчика {1} и ожидать ошибку {0}")
    public void deleteGoalAndExpectError(IExpectedError error, Long counterId, Long goalId) {
        deleteGoal(ERROR_MESSAGE, expectError(error), counterId, goalId);
    }

    private ManagementV1CounterCounterIdGoalGoalIdDELETESchema deleteGoal(String message, Matcher matcher,
                                                                          Long counterId, Long goalId) {
        ManagementV1CounterCounterIdGoalGoalIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/goal/%s", counterId, goalId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1CounterCounterIdGoalGoalIdDELETESchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Проверить наличие целей у пользователя")
    public InternalManagementV1CounterCheckGoalsGETSchema checkGoalsExistence() {
        return checkGoals(SUCCESS_MESSAGE, expectSuccess());
    }

    private InternalManagementV1CounterCheckGoalsGETSchema checkGoals(String message, Matcher matcher) {
        InternalManagementV1CounterCheckGoalsGETSchema result = executeAsJson(
                getRequestBuilder("/internal/management/v1/counter/check_goals").
                        get()
        ).readResponse(InternalManagementV1CounterCheckGoalsGETSchema.class);

        assertThat(message, result, matcher);
        return result;
    }

}
