package ru.yandex.autotests.metrika.steps.management;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import com.google.common.base.Joiner;
import org.hamcrest.Matcher;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.InternalCounterCounterIdMovePUTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCheckBigGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalRbacRankGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalRbacRankPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdDELETESchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdMovePUTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdOfflineReachReadyPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdPUTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdUndeletePOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CountersFlagsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CountersFlagsPOSTPUTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CountersFlagsPOSTPUTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CountersGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CountersPOSTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CountersPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1LabelsCountersNumSpecialGETSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.parameters.internal.CheckBigParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.RankParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.api.management.client.counter.SpecialLabels;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;

/**
 * Created by proxeter on 28.07.2014.
 */
public class CountersSteps extends MetrikaBaseSteps {

    @Step("Получить данные счетчика {0}")
    public CounterFull getCounterInfo(Long counterId, IFormParameters... parameters) {
        return getCounterInfo(SUCCESS_MESSAGE, expectSuccess(), counterId, parameters).getCounter();
    }

    @Step("Получить статус большой счетчик или нет {0}")
    public Boolean getCounterBignessStatus(Long counterId, IFormParameters... parameters) {
        InternalManagementV1CounterCheckBigGETSchema result = executeAsJson(
                getRequestBuilder(format("/internal/management/v1/counter/check_big", counterId)).get(aggregate(
                        new CheckBigParameters()
                                .withCounterId(counterId),
                        parameters)))
                .readResponse(InternalManagementV1CounterCheckBigGETSchema.class);
        return result.getCounters().get(counterId.intValue());
    }

    @Step("Получить данные счетчика {1} и ожидать ошибку {0}")
    public CounterFull getCounterInfoAndExpectError(IExpectedError error,
                                                    Long counterId,
                                                    IFormParameters... parameters) {
        return getCounterInfo(ERROR_MESSAGE, expectError(error), counterId, parameters).getCounter();
    }

    private ManagementV1CounterCounterIdGETSchema getCounterInfo(String message, Matcher matcher,
                                                                 Long counterId, IFormParameters... parameters) {
        ManagementV1CounterCounterIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s", counterId)).get(parameters))
                .readResponse(ManagementV1CounterCounterIdGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить список доступных счетчиков")
    public List<CounterBrief> getAvailableCountersAndExpectSuccess(IFormParameters... parameters) {
        return getAvailableCounters(SUCCESS_MESSAGE, expectSuccess(), parameters).getCounters();
    }

    @Step("Получить список доступных счетчиков и ожидать ошибку {0}")
    public List<CounterBrief> getAvailableCountersAndExpectError(IExpectedError error,
                                                                 IFormParameters... parameters) {
        return getAvailableCounters(ERROR_MESSAGE, expectError(error), parameters).getCounters();
    }

    @Step("Получить количество счетчиков с параметрами {0}")
    public long getCountersAmountAndExceptSuccess(IFormParameters... parameters) {
        return getAvailableCounters(SUCCESS_MESSAGE, expectSuccess(), parameters).getRows();
    }

    private ManagementV1CountersGETSchema getAvailableCounters(String message, Matcher matcher,
                                                               IFormParameters... parameters) {
        ManagementV1CountersGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/counters").get(parameters))
                .readResponse(ManagementV1CountersGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить количество счетчиков по группам")
    public SpecialLabels getCountersByGroupsAndExpectSuccess(IFormParameters... parameters) {
        return getCountersAmountByGroups(SUCCESS_MESSAGE, expectSuccess(), parameters).getResponse();
    }

    @Step("Получить количество счетчиков по группам и ожидать ошибку {0}")
    public SpecialLabels getCountersAmountByGroupsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getCountersAmountByGroups(ERROR_MESSAGE, expectError(error), parameters).getResponse();
    }

    private ManagementV1LabelsCountersNumSpecialGETSchema getCountersAmountByGroups(String message, Matcher matcher,
                                                                                    IFormParameters... parameters) {
        ManagementV1LabelsCountersNumSpecialGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/labels/counters_num/special").get(parameters))
                .readResponse(ManagementV1LabelsCountersNumSpecialGETSchema.class);

        assertThat(message, result, matcher);
        return result;
    }

    @Step("Получить счетчик {0} из списка")
    public CounterBrief getCounterFromList(Long counterId,
                                           IFormParameters... parameters) {
        List<CounterBrief> availableCounters =
                getAvailableCountersAndExpectSuccess(parameters);

        availableCounters = availableCounters.stream()
                .filter(counter -> counter.getId().equals(counterId))
                .collect(toList());

        assumeThat(format("счетчик с id %s есть в списке", counterId), availableCounters.size(), equalTo(1));

        return availableCounters.get(0);
    }

    @Step("Добавить счетчик")
    public CounterFull addCounterAndExpectSuccess(
            CounterFull counter, IFormParameters... parameters) {
        return addCounter(SUCCESS_MESSAGE, expectSuccess(), counter, parameters);
    }

    @Step("Добавить счетчики")
    public List<CounterFull> addCounters(List<CounterFull> counters, IFormParameters... parameters) {
        return counters.stream().map(counter -> addCounterAndExpectSuccess(counter, parameters)).collect(Collectors.toList());
    }

    @Step("Добавить счетчик и ожидать ошибку {0}")
    public CounterFull addCounterAndExpectError(
            IExpectedError error,
            CounterFull counter, IFormParameters... parameters) {
        return addCounter(ERROR_MESSAGE, expectError(error), counter, parameters);
    }

    private CounterFull addCounter(
            String message, Matcher matcher,
            CounterFull counter, IFormParameters... parameters) {

        ManagementV1CountersPOSTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/counters")
                        .post(
                                new ManagementV1CountersPOSTRequestSchema().withCounter(counter),
                                parameters))
                .readResponse(ManagementV1CountersPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getCounter();
    }

    @Step("Задать счетчику {0} ранг {1}")
    public Long setRankAndExpectSuccess(
            Long counterId, Long rank, IFormParameters... parameters) {
        return setRank(SUCCESS_MESSAGE, expectSuccess(), counterId, rank, parameters).getRank();
    }

    @Step("Задать счетчику {1} ранг {2} и ожидать ошибку {0}")
    public Long setRankAndExpectError(
            IExpectedError error,
            Long counterId, Long rank, IFormParameters... parameters) {
        return setRank(ERROR_MESSAGE, expectError(error), counterId, rank, parameters).getRank();
    }

    private InternalRbacRankPOSTSchema setRank(
            String message, Matcher matcher,
            Long counterId, Long rank, IFormParameters... parameters) {

        InternalRbacRankPOSTSchema result = executeAsJson(
                getRequestBuilder("/internal/rbac/rank")
                        .post(new EmptyHttpEntity(), aggregate(
                                new RankParameters()
                                        .withCounterId(counterId)
                                        .withRank(rank),
                                parameters)))
                .readResponse(InternalRbacRankPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить ранг счетчика {0}")
    public Long getRankAndExpectSuccess(
            Long counterId, IFormParameters... parameters) {
        return getRank(SUCCESS_MESSAGE, expectSuccess(), counterId, parameters).getRank();
    }

    private InternalRbacRankGETSchema getRank(String message, Matcher matcher,
                                              Long counterId, IFormParameters... parameters) {
        InternalRbacRankGETSchema result = executeAsJson(
                getRequestBuilder("/internal/rbac/rank").get(
                        aggregate(new RankParameters().withCounterId(counterId),
                                parameters)))
                .readResponse(InternalRbacRankGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить счетчик {0}")
    public Boolean deleteCounterAndExpectSuccess(Long counterId) {
        if (counterId == null) {
            // Не надо удалять счетчик, если couneterId == null
            return false;
        }

        return deleteCounter(SUCCESS_MESSAGE, expectSuccess(), counterId);
    }

    @Step("Удалить счетчик {0} и ожидать ошибку {1}")
    public void deleteCounterAndExpeсtError(Long counterId, IExpectedError error) {
        if (counterId != null) {
            deleteCounter(ERROR_MESSAGE, expectError(error), counterId);
        }
    }

    @Step("Удалить счетчики")
    public List<Boolean> deleteCounters(List<Long> counterIds) {
        if (counterIds != null) {
            return counterIds.stream().map(this::deleteCounterAndExpectSuccess).collect(Collectors.toList());
        }
        return Collections.emptyList();
    }

    @Step("Удалить счетчик {0} и игнорировать результат")
    public Boolean deleteCounterAndIgnoreStatus(Long counterId) {
        if (counterId == null) {
            return false;
        }

        return deleteCounter(ANYTHING_MESSAGE, expectAnything(), counterId);
    }

    private Boolean deleteCounter(String message, Matcher matcher,
                                  Long counterId, IFormParameters... parameters) {
        ManagementV1CounterCounterIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s", counterId))
                        .delete(aggregate(parameters)))
                .readResponse(ManagementV1CounterCounterIdDELETESchema.class);

        assertThat(message, result, matcher);

        return result.getSuccess();
    }

    @Step("Восстановление счетчика {0}")
    public Boolean undeleteCounter(Long counterId) {
        ManagementV1CounterCounterIdUndeletePOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/undelete", counterId))
                        .post(new EmptyHttpEntity(), EMPTY_CONTEXT))
                .readResponse(ManagementV1CounterCounterIdUndeletePOSTSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getSuccess();
    }

    @Step("Удаление всех счетчиков с именем: {0}")
    public void deleteAllCountersWithName(String name) {
        List<CounterBrief> availableCounters = getAvailableCountersAndExpectSuccess();
        for (CounterBrief counter : availableCounters) {
            if (counter.getName() == null) {
                continue;
            }
            if (counter.getName().equals(name)) {
                deleteCounterAndExpectSuccess(counter.getId());
            }
        }
    }

    @Step("Удаление всех счетчиков")
    public void deleteAllCounters() {
        deleteCounters(getAvailableCountersAndExpectSuccess().stream()
                .mapToLong(CounterBrief::getId).boxed().collect(toList()));
    }

    @Step("Изменить счетчик {0}")
    public CounterFull editCounter(
            Long counterId, CounterFull counter,
            IFormParameters... parameters) {
        return editCounter(SUCCESS_MESSAGE, expectSuccess(), counterId, counter, parameters);
    }

    @Step("Изменить счетчик {1} и ожидать ошибку {0}")
    public CounterFull editCounterAndExpectError(
            IExpectedError error,
            Long counterId, CounterFull counter,
            IFormParameters... parameters) {
        return editCounter(ERROR_MESSAGE, expectError(error), counterId, counter, parameters);
    }

    private CounterFull editCounter(
            String message,
            Matcher matcher,
            Long counterId,
            CounterFull counter,
            IFormParameters... parameters) {

        ManagementV1CounterCounterIdPUTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s", counterId))
                        .put(
                                new ManagementV1CountersPOSTRequestSchema().withCounter(counter),
                                parameters))
                .readResponse(ManagementV1CounterCounterIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result.getCounter();
    }

    @Step("Перенести счетчик {0} на логин {1}")
    public Boolean moveCounter(Long counterId, String login, IFormParameters... parameters) {
        return moveCounter(SUCCESS_MESSAGE, expectSuccess(), counterId, login, parameters);
    }

    @Step("Перенести счетчик {1} на логин {2} и ожидать ошибку {0}")
    public Boolean moveCounterAndExpectError(ManagementError error,
                                             Long counterId, String login,
                                             IFormParameters... parameters) {
        return moveCounter(ERROR_MESSAGE, expectError(error), counterId, login, parameters);
    }

    private Boolean moveCounter(String message, Matcher matcher,
                                Long counterId, String login, IFormParameters... parameters) {

        ManagementV1CounterCounterIdMovePUTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/move", counterId))
                        .put(new EmptyHttpEntity(), makeParameters("to_login", login).append(parameters)))
                .readResponse(ManagementV1CounterCounterIdMovePUTSchema.class);

        assertThat(message, result, matcher);

        return result.getSuccess();
    }

    @Step("Отобрать счетчик {1} на логин {2} и ожидать ошибку {0}")
    public Boolean move2CounterAndExpectError(ManagementError error,
                                              Long counterId, String domain, String login,
                                              IFormParameters... parameters) {
        return move2Counter(ERROR_MESSAGE, expectError(error), counterId, domain, login, parameters);
    }

    private Boolean move2Counter(String message, Matcher matcher,
                                 Long counterId, String domain, String login, IFormParameters... parameters) {

        InternalCounterCounterIdMovePUTSchema result = executeAsJson(
                getRequestBuilder(String.format("/internal/counter/%s/move", counterId))
                        .put(new EmptyHttpEntity(),
                                makeParameters("domain", domain).append("ulogin", login).append(parameters)))
                .readResponse(InternalCounterCounterIdMovePUTSchema.class);

        assertThat(message, result, matcher);

        return result.getSuccess();
    }

    @Step("Включить мониторинг для счётчика {0}")
    public void setMonitoringEnabledFor(long counterId, CounterFull counter, IFormParameters... parameters) {
        counter.getMonitoring().setEnableMonitoring(1L);
        editCounter(counterId, counter, parameters);
    }

    @Step("Включить offline_reach для счетчика {0}")
    public Boolean enableOffliReachFeature(long counterId, IFormParameters... parameters) {
        ManagementV1CounterCounterIdOfflineReachReadyPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%d/offline_reach_ready", counterId)).post(parameters)
        ).readResponse(ManagementV1CounterCounterIdOfflineReachReadyPOSTSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getSuccess();
    }

    @Step("Получить флаги счетчика")
    public List<CounterFlags> getCounterFlagsAndExpectSuccess(List<Long> counterIds) {
        ManagementV1CountersFlagsGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/counters/flags")
                        .get(makeParameters("ids", Joiner.on(",").join(counterIds)))
        ).readResponse(ManagementV1CountersFlagsGETSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getFlags();
    }

    @Step("Изменить флаги счетчика")
    public List<CounterFlags> editCounterFlagsAndExpectSuccess(List<CounterFlags> flags) {
        ManagementV1CountersFlagsPOSTPUTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/counters/flags")
                        .put(new ManagementV1CountersFlagsPOSTPUTRequestSchema().withFlags(flags))
        ).readResponse(ManagementV1CountersFlagsPOSTPUTSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getFlags();
    }

    @Step("Изменить флаги счетчика")
    public List<CounterFlags> editCounterFlagsAndExpectError(List<CounterFlags> flags, Matcher matcher) {
        ManagementV1CountersFlagsPOSTPUTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/counters/flags")
                        .put(new ManagementV1CountersFlagsPOSTPUTRequestSchema().withFlags(flags))
        ).readResponse(ManagementV1CountersFlagsPOSTPUTSchema.class);

        assertThat(ERROR_MESSAGE, result, matcher);

        return result.getFlags();
    }

    @Step("Попытаться создать счетчик с пустым телом запроса")
    public void tryCreateCounterWithEmptyBody(IExpectedError expectedError) {
        ManagementV1CountersPOSTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/counters")
                        .post(new EmptyHttpEntity(), makeParameters())
        ).readResponse(ManagementV1CountersPOSTSchema.class);

        assertThat(ERROR_MESSAGE, result, expectError(expectedError));
    }
}
