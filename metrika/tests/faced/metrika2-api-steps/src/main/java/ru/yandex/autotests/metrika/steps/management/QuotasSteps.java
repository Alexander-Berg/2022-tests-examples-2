package ru.yandex.autotests.metrika.steps.management;

import ru.yandex.autotests.metrika.beans.schemes.ManagementV1QuotasGETSchema;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.QuotaControllerInnerQuotas;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by sourx on 12.01.2016.
 */
public class QuotasSteps extends MetrikaBaseSteps {

    @Step("Получить список с лимитами")
    public QuotaControllerInnerQuotas getQuotas() {
        ManagementV1QuotasGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/quotas").get())
                .readResponse(ManagementV1QuotasGETSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getQuotas();
    }
}
