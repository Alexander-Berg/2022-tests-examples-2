package ru.yandex.autotests.internalapid.steps;

import java.net.URL;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import com.google.common.base.Joiner;
import com.google.gson.JsonArray;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.hamcrest.Matcher;
import org.joda.time.DateTime;
import org.joda.time.LocalDate;
import org.joda.time.LocalDateTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.internalapid.beans.responses.DirectUpdatedUserCountersNumResponse;
import ru.yandex.autotests.internalapid.beans.responses.DirectUserCountersNumExtendedResponse;
import ru.yandex.autotests.internalapid.beans.responses.DirectUserCountersNumResponse;
import ru.yandex.autotests.internalapid.beans.responses.DirectUsersCountersNumAdditionalResponse;
import ru.yandex.autotests.internalapid.beans.responses.ListResponse;
import ru.yandex.autotests.internalapid.beans.schemes.CountersV1ExistentCountersPOSTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.CountersV1ExistentCountersPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.DirectGetGoalCountsGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.DirectTurnOnCallTrackingPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.DisplayCreateNewGoalGETRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.GoalsV1CounterGoalsGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.GrantsV1GrantRequestsPOSTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.GrantsV1GrantRequestsPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.GrantsV1UserUidGrantAccessRequestsStatusPOSTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.GrantsV1UserUidGrantAccessRequestsStatusPOSTSchema;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.api.management.client.AddGrantRequest;
import ru.yandex.metrika.api.management.client.GrantRequestServiceInnerGrantRequestStatus;
import ru.yandex.metrika.api.management.client.GrantRequestServiceInnerGrantResult;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.internalapid.common.ExistentCounter;
import ru.yandex.metrika.internalapid.direct.external.CounterGoal;
import ru.yandex.metrika.internalapid.direct.external.CounterGoalCount;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class DirectSteps extends HttpClientLiteFacade {

    private final static DateTimeFormatter FORMAT = DateTimeFormat.forPattern("yyyy-MM-dd");

    public DirectSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Вызвать ручку /direct/user_counters_num")
    public ListResponse<DirectUserCountersNumResponse> getDirectUserCountersNum(List<Long> uids) {
        List<?> list = get(List.class,
                "/direct/user_counters_num",
                new FreeFormParameters().append("uids", uids.stream().map(Object::toString).collect(Collectors.joining(",")))
        );
        ListResponse<DirectUserCountersNumResponse> response = new ListResponse<>();

        response.parseFromList(list, DirectUserCountersNumResponse::parseFrom);
        return response;
    }

    @Step("Вызвать ручку /direct/user_counters_num2")
    public DirectUsersCountersNumAdditionalResponse getDirectUserCountersNum2(List<Long> uids, Optional<Integer> limit, String prefix, List<Integer> counterIds) {
        FreeFormParameters parameters = new FreeFormParameters().append("uids",
                uids.stream().map(Object::toString).collect(Collectors.joining(",")));
        limit.ifPresent(l -> parameters.append("limit",  l));
        if (StringUtils.isNotEmpty(prefix)) parameters.append("prefix", prefix);
        if (CollectionUtils.isNotEmpty(counterIds)) parameters.append("counterIds", counterIds.stream().map(Object::toString).collect(Collectors.joining(",")));
        Object o = get(Object.class,
                "/direct/user_counters_num2",
                parameters
        );
        return DirectUsersCountersNumAdditionalResponse.parseFrom(o);
    }

    @Step("Вызвать ручку /direct/user_counters_num_extended")
    public ListResponse<DirectUserCountersNumExtendedResponse> getDirectUserCountersNumExtended(List<Long> uids) {
        List<?> list = get(List.class,
                "/direct/user_counters_num_extended",
                new FreeFormParameters().append("uids", uids.stream().map(Object::toString).collect(Collectors.joining(",")))
        );
        ListResponse<DirectUserCountersNumExtendedResponse> response = new ListResponse<>();

        response.parseFromList(list, DirectUserCountersNumExtendedResponse::parseFrom);
        return response;
    }

    @Step("Вызвать ручку /direct/updated_user_counters_num")
    public ListResponse<DirectUpdatedUserCountersNumResponse> getDirectUpdatedUserCountersNum(LocalDateTime lastTime) {
        final String lastTimeStr = lastTime.toString(DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss"));
        List<?> list = get(List.class, "/direct/updated_user_counters_num", new FreeFormParameters().append("last_time", lastTimeStr));
        ListResponse<DirectUpdatedUserCountersNumResponse> response = new ListResponse<>();

        response.parseFromList(list, DirectUpdatedUserCountersNumResponse::parseFrom);
        return response;
    }

    @Step("Создать цель через /display/create_new_goal")
    public GoalE addDisplayGoal(long counterId, GoalE goal) {
        return post(DisplayCreateNewGoalGETRequestSchema.class,
                "/display/create_new_goal",
                new DisplayCreateNewGoalGETRequestSchema().withGoal(goal),
                new FreeFormParameters().append("counter_id", counterId)
        ).getGoal();
    }

    @Step("Получить измененные цели")
    public List<Integer> getChangedGoalsIds(DateTime lastTime) {
        final String lastTimeStr = lastTime.toString(DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss"));
        JsonArray result = get(JsonArray.class, "/direct/changed_goals",
                new FreeFormParameters().append("last_time", lastTimeStr));
        return StreamSupport.stream(result.spliterator(), false).map(el -> el.getAsJsonObject().get("goal_id").getAsInt()).collect(Collectors.toList());
    }

    @Step("Получить цели счетчиков")
    public List<CounterGoal> getCounterGoals(List<Long> counterIds) {
        return get(GoalsV1CounterGoalsGETSchema.class, "/goals/v1/counter_goals",
                new FreeFormParameters().append("counters", counterIds.stream().map(Object::toString).collect(Collectors.joining(",")))).getGoals();
    }

    @Step("Получить цели счетчиков через директ")
    public List<CounterGoal> getCounterGoalsDirect(List<Long> counterIds) {
        return get(GoalsV1CounterGoalsGETSchema.class, "/direct/counter_goals",
                new FreeFormParameters().append("counters", counterIds.stream().map(Object::toString).collect(Collectors.joining(",")))).getGoals();
    }

    @Step("Добавить гранты через /grants/v1/grant_requests")
    public List<GrantRequestServiceInnerGrantResult> addGrants(List<AddGrantRequest> requests) {
        return post(GrantsV1GrantRequestsPOSTSchema.class,
                "/grants/v1/grant_requests",
                new GrantsV1GrantRequestsPOSTRequestSchema().withRequests(requests)).getResponse();
    }

    @Step("Юзеру uid {0}, показать статус доступности к счетчикам {1}")
    public List<GrantRequestServiceInnerGrantRequestStatus> postGrantAccessRequestsStatusAndExpectSuccess(long uid, List<Long> counterIdList) {
        return post(GrantsV1UserUidGrantAccessRequestsStatusPOSTSchema.class,
                String.format("/grants/v1/user/%d/grant_access_requests_status", uid),
                new GrantsV1UserUidGrantAccessRequestsStatusPOSTRequestSchema().withCounterIdList(counterIdList)
        ).getGrantRequestStatusList();
    }

    @Step("Взять список счетчиков, в нынешном кейсе, они вот => {0}. И вернуть из этого списка только существующие счетчики")
    public List<ExistentCounter> getExistentCountersAndExpectSuccess(List<Long> counterIdList) {
        return getExistentCounters(counterIdList, SUCCESS_MESSAGE, expectSuccess()).getResponse();
    }

    @Step("Взять список счетчиков, размер которого больше допустимого и вернуть соответственно ошибку")
    public void getExistentCountersAndExpectError(List<Long> counterIdList, IExpectedError error) {
        getExistentCounters(counterIdList, ERROR_MESSAGE, expectError(error)).getResponse();
    }

    private CountersV1ExistentCountersPOSTSchema getExistentCounters(List<Long> counterIdList, String message, Matcher matcher, IFormParameters... parameters) {
        CountersV1ExistentCountersPOSTSchema result = post(
                CountersV1ExistentCountersPOSTSchema.class,
                "/counters/v1/existent_counters",
                new CountersV1ExistentCountersPOSTRequestSchema().withCounterIdList(counterIdList)
        );

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Включить call tracking через /direct/turn_on_call_tracking")
    public GoalE turnOnCallTracking(long counterId) {
        return post(DirectTurnOnCallTrackingPOSTSchema.class,
                "/direct/turn_on_call_tracking",null,
                new FreeFormParameters().append("counterId", counterId)).getGoal();
    }

    @Step("Получить список счетчиков-целей и количеств достижений целей через /direct/get_goal_counts")
    public List<CounterGoalCount> getCounterGoalsReaches(List<Integer> counterIds, LocalDate startDate, LocalDate endDate) {
        return get(DirectGetGoalCountsGETSchema.class,
        "/direct/get_goal_counts",
        new FreeFormParameters()
                .append("counterIds", Joiner.on(",").join(counterIds))
                .append("startDate", FORMAT.print(startDate))
                .append("endDate", FORMAT.print(endDate))
        ).getResponse();
    }
}
