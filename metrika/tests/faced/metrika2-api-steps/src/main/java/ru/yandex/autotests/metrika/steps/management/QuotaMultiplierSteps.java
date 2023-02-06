package ru.yandex.autotests.metrika.steps.management;

import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdGrantMultiplierGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1DelegateMultiplierGETSchema;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class QuotaMultiplierSteps extends MetrikaBaseSteps {

    @Step("Получить множитель на гранты")
    public double getGrantQuotaMultiplier(Long counterId) {
        ManagementV1CounterCounterIdGrantMultiplierGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grant_multiplier", counterId)).get()
        ).readResponse(ManagementV1CounterCounterIdGrantMultiplierGETSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getMultiplier();
    }

    @Step("Получить множитель на представителей")
    public double getDelegateQuotaMultiplier() {
        ManagementV1DelegateMultiplierGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/delegate_multiplier").get()
        ).readResponse(ManagementV1DelegateMultiplierGETSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getMultiplier();
    }
}
