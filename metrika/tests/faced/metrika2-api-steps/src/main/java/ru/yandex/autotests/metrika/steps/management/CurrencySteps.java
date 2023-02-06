package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdCurrencyGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdCurrencyGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFilterFilterIdDELETESchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFiltersGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFiltersPOSTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdFiltersPOSTSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.filter.FilterE;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addJsonAttachment;

/**
 * Created by okunev on 08.09.2015.
 */
public class CurrencySteps extends MetrikaBaseSteps {

    @Step("Получить список валют для счетчика {0}")
    public List<Currency> getCurrency(Long counterId) {
        return getFilters(SUCCESS_MESSAGE, expectSuccess(), counterId).getCurrency();
    }

    private ManagementV1CounterCounterIdCurrencyGETSchema getFilters(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdCurrencyGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/currency", counterId)).get())
                .readResponse(ManagementV1CounterCounterIdCurrencyGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

}
