package ru.yandex.autotests.internalapid.steps;

import java.net.URL;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import com.google.common.base.Joiner;
import com.google.gson.JsonObject;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.internalapid.beans.responses.InternalApidResponse;
import ru.yandex.autotests.internalapid.beans.responses.ListResponse;
import ru.yandex.autotests.internalapid.beans.responses.MarketAnalyticsCheckAccessResponse;
import ru.yandex.autotests.internalapid.beans.schemes.CounterAccessGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesAddCounterPOSTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesAddCounterPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCounterCounterIdGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCounterCounterIdGrantsBatchPOSTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCounterCounterIdGrantsBatchPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCounterCounterIdGrantsGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCounterCounterIdGrantsPOSTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCounterCounterIdGrantsPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCounterIdGoalsGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesCountersGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesDeleteCounterCounterIdDELETESchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesEditCounterCounterIdPUTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesEditCounterCounterIdPUTSchema;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.metrika.api.management.client.counter.CounterEdit;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterType;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class InternalApiSteps extends HttpClientLiteFacade {

    public InternalApiSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }


//    @Step("Добавить счетчик")
//    public CounterFull addCounterAndExpectSuccess(
//            CounterFull counter, IFormParameters... parameters) {
//        return addCounter(SUCCESS_MESSAGE, expectSuccess(), counter, parameters);
//    }
//
//    @Step("Добавить счетчики")
//    public List<CounterFull> addCounters(List<CounterFull> counters, IFormParameters... parameters) {
//        return counters.stream().map(counter -> addCounterAndExpectSuccess(counter, parameters)).collect(Collectors.toList());
//    }
//
//    @Step("Добавить счетчик и ожидать ошибку {0}")
//    public CounterFull addCounterAndExpectError(
//            IExpectedError error,
//            CounterFull counter, IFormParameters... parameters) {
//        return addCounter(ERROR_MESSAGE, expectError(error), counter, parameters);
//    }
//
//    private CounterFull addCounter(
//            String message, Matcher matcher,
//            CounterFull counter, IFormParameters... parameters) {
//
//        ManagementV1CountersPOSTSchema result = executeAsJson(
//                getRequestBuilder("/management/v1/counters")
//                        .post(
//                                new ManagementV1CountersPOSTRequestSchema().withCounter(counter),
//                                parameters))
//                .readResponse(ManagementV1CountersPOSTSchema.class);
//
//        assertThat(message, result, matcher);
//
//        return result.getCounter();
//    }


    @Step("Получить наличие доступа пользователя {1} к счетчику {0}")
    public boolean getCounterAccess(long counterId, String login) {
        FreeFormParameters params = new FreeFormParameters().append("staff_login", login).append("counter_id", counterId);
        return getCounterAccess(params);
    }

    @Step("Вызвать ручку /counter_access")
    public boolean getCounterAccess(IFormParameters... parameters) {
        return getAndExpectSuccess(CounterAccessGETSchema.class, "/counter_access", parameters).getAccess();
    }

    @Step("Вызвать ручку /bs_hosts")
    public String getBsHosts(IFormParameters... parameters) {
        return get(String.class, "/bs_hosts", parameters);
    }

    @Step("Вызвать ручку /tvm")
    public String getTvm(IFormParameters... parameters) {
        return get(String.class, "/tvm", parameters);
    }

    @SuppressWarnings("unchecked")
    @Step("Вызвать ручку /market_analytics/check_access")
    public ListResponse<MarketAnalyticsCheckAccessResponse> getCheckAccess(Map<String, List<MarketAnalyticsCheckAccessResponse>> body) {
        ListResponse post = post(ListResponse.class, "/market_analytics/check_access", body);
        post.parseFromList(post.getResult(), o -> new MarketAnalyticsCheckAccessResponse(
                ((Number) ((Map<?, ?>) o).get("counter_id")).intValue(),
                ((List<? extends Number>) ((Map<?, ?>) o).get("uids")).stream().map(Number::longValue).collect(Collectors.toList()))
        );
        return post;
    }

    @Step("Создать счетчик через ручку /yandexservices/add_counter")
    public CounterFull createCounter(CounterFull counterFull) {
        YandexservicesAddCounterPOSTSchema response = post(
                YandexservicesAddCounterPOSTSchema.class,
                "/yandexservices/add_counter",
                new YandexservicesAddCounterPOSTRequestSchema().withCounter(counterFull)
        );
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());
        return response.getCounter();
    }

    @Step("Попытаться создать счетчик через ручку /yandexservices/add_counter")
    public YandexservicesAddCounterPOSTSchema tryCreateCounter(CounterFull counterFull) {
        return post(YandexservicesAddCounterPOSTSchema.class, "/yandexservices/add_counter", new YandexservicesAddCounterPOSTRequestSchema().withCounter(counterFull));
    }

    @Step("Изменить счетчик через ручку /yandexservices/edit_counter/{0}")
    public CounterFull editCounter(long counterId, CounterEdit counterEdit) {
        return put(YandexservicesEditCounterCounterIdPUTSchema.class, String.format("/yandexservices/edit_counter/%d", counterId), new YandexservicesEditCounterCounterIdPUTRequestSchema().withCounter(counterEdit)).getCounter();
    }

    @Step("Удалить счетчик через ручку /yandexservices/delete_counter/{0}")
    public void deleteCounter(long counterId) {
        YandexservicesDeleteCounterCounterIdDELETESchema response =
                delete(YandexservicesDeleteCounterCounterIdDELETESchema.class, String.format("/yandexservices/delete_counter/%d", counterId));
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());
    }

    @Step("Просмотреть счетчик через ручку /yandexservices/counter/{0}")
    public CounterFull сounter(long counterId) {
        return get(YandexservicesCounterCounterIdGETSchema.class, String.format("/yandexservices/counter/%d", counterId)).getCounter();
    }

    @Step("Просмотреть счетчик через ручку /yandexservices/counters")
    public List<CounterBrief> counters(String exactName) {
        return get(YandexservicesCountersGETSchema.class, "/yandexservices/counters",
                new FreeFormParameters().append("exact_name", exactName)
        ).getCounters();
    }

    @Step("Просмотреть цели через ручку /yandexservices/{0}/goals")
    public List<GoalE> goals(long counterId) {
        return get(YandexservicesCounterIdGoalsGETSchema.class, String.format("/yandexservices/%d/goals/", counterId)).getGoals();

    }

    public <T> T getAndExpectSuccess(Class<T> responseTypeClass, String path, IFormParameters... parameterses) {
        T response = get(responseTypeClass, path, parameterses);

        //noinspection unchecked
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());

        return response;
    }

    @Step("Добавить доступ {1} через ручку /yandexservices/counter/{0}/grants")
    public GrantE addGrant(long counterId, GrantE grant) {
        return post(
                YandexservicesCounterCounterIdGrantsPOSTSchema.class,
                String.format("/yandexservices/counter/%s/grants", counterId),
                new YandexservicesCounterCounterIdGrantsPOSTRequestSchema().withGrant(grant)
        ).getGrant();
    }

    @Step("Добавить доступы {1} через ручку /yandexservices/counter/{0}/grants_batch")
    public List<GrantE> addGrants(long counterId, List<GrantE> grants) {
        return post(
                YandexservicesCounterCounterIdGrantsBatchPOSTRequestSchema.class,
                String.format("/yandexservices/counter/%s/grants_batch", counterId),
                new YandexservicesCounterCounterIdGrantsBatchPOSTSchema().withGrants(grants)
        ).getGrants();
    }

    @Step("Изменить доступы {1} через ручку /yandexservices/counter/{0}/grants_batch")
    public List<GrantE> editGrants(long counterId, List<GrantE> grants) {
        return put(
                YandexservicesCounterCounterIdGrantsBatchPOSTRequestSchema.class,
                String.format("/yandexservices/counter/%s/grants_batch", counterId),
                new YandexservicesCounterCounterIdGrantsBatchPOSTSchema().withGrants(grants)
        ).getGrants();
    }

    @Step("Удалить доступы {1} через ручку /yandexservices/counter/{0}/grants_batch")
    public void deleteGrants(long counterId, List<String> logins) {
        delete(
                JsonObject.class,
                String.format("/yandexservices/counter/%s/grants_batch", counterId),
                new FreeFormParameters().append("user_logins", Joiner.on(",").join(logins))
        );
    }

    @Step("Изменить доступ {1} через ручку /yandexservices/counter/{0}/grants")
    public GrantE editGrant(long counterId, GrantE grant) {
        return put(
                YandexservicesCounterCounterIdGrantsPOSTSchema.class,
                String.format("/yandexservices/counter/%s/grants", counterId),
                new YandexservicesCounterCounterIdGrantsPOSTRequestSchema().withGrant(grant)
        ).getGrant();
    }

    @Step("Удалить доступ пользователю {1} через ручку /yandexservices/counter/{0}/grants")
    public void deleteGrant(long counterId, String login) {
        delete(
                JsonObject.class,
                String.format("/yandexservices/counter/%s/grants", counterId),
                new FreeFormParameters().append("user_login", login)
        );
    }

    @Step("Получить список доступов на счетчик {0}")
    public List<GrantE> getGrants(long counterId) {
        return get(YandexservicesCounterCounterIdGrantsGETSchema.class,
                String.format("/yandexservices/counter/%s/grants", counterId)).getGrants();
    }
}
