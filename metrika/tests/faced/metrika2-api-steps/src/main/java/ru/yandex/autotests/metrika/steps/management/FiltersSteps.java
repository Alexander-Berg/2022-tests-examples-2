package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFilterFilterIdDELETESchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFiltersGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFiltersPOSTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFiltersPOSTSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.filter.FilterE;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addJsonAttachment;

/**
 * Created by okunev on 08.09.2015.
 */
public class FiltersSteps extends MetrikaBaseSteps {

    @Step("Получить список фильтров для счетчика {0}")
    public List<FilterE> getFilters(Long counterId) {
        return getFilters(SUCCESS_MESSAGE, expectSuccess(), counterId).getFilters();
    }

    private ManagementV1CounterCounterIdFiltersGETSchema getFilters(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdFiltersGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/filters", counterId)).get())
                .readResponse(ManagementV1CounterCounterIdFiltersGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать фильтры для счетчика {0}")
    public List<FilterE> addFilters(Long counterId, List<FilterE> filters) {
        addJsonAttachment(String.format("Всего фильтров %s", filters.size()), JsonUtils.toString(filters));

        return filters.stream().map(filter -> addFilter(counterId, filter)).collect(toList());
    }

    @Step("Создать фильтр для счетчика {0}")
    public FilterE addFilter(Long counterId, FilterE filter) {
        return addFilter(SUCCESS_MESSAGE, expectSuccess(), counterId, filter).getFilter();
    }

    @Step("Создать фильтр для счетчика {1} и ожидать ошибку {0}")
    public FilterE addFilterAndExpectError(IExpectedError error, Long counterId, FilterE filter) {
        return addFilter(ERROR_MESSAGE, expectError(error), counterId, filter).getFilter();
    }

    private ManagementV1CounterCounterIdFiltersPOSTSchema addFilter(String message, Matcher matcher,
                                                                    Long counterId, FilterE filter) {
        ManagementV1CounterCounterIdFiltersPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/filters", counterId))
                        .post(new ManagementV1CounterCounterIdFiltersPOSTRequestSchema().withFilter(filter)))
                .readResponse(ManagementV1CounterCounterIdFiltersPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить фильтры у счетчика {0}")
    public void deleteFilters(Long counterId, List<FilterE> filters) {
        addJsonAttachment(String.format("Всего фильтров %s", filters.size()), JsonUtils.toString(filters));

        filters.forEach(filter -> deleteFilter(counterId, filter.getId()));
    }

    @Step("Удалить фильтр {1} счетчика {0}")
    public void deleteFilter(Long counterId, Long filterId) {
        if (filterId != null) {
            deleteFilter(SUCCESS_MESSAGE, expectSuccess(), counterId, filterId);
        }
    }

    private ManagementV1CounterCounterIdFilterFilterIdDELETESchema deleteFilter(String message, Matcher matcher,
                                                                                Long counterId, Long filterId) {
        ManagementV1CounterCounterIdFilterFilterIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/filter/%s", counterId, filterId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1CounterCounterIdFilterFilterIdDELETESchema.class);

        assertThat(message, result, matcher);

        return result;
    }

}
