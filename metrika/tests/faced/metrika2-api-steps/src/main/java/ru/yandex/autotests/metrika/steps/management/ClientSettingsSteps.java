package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.ClientSettingsObjectWrapper;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1ClientSettingsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1ClientSettingsPOSTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1ClientSettingsPOSTSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.ClientSettings;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by omatikaya on 03.02.17.
 */
public class ClientSettingsSteps extends MetrikaBaseSteps {

    @Step("Получить настройки рассылки")
    public ClientSettings getClientSettingsAndExpectSuccess(IFormParameters... parameters) {
        return getClientSettings(SUCCESS_MESSAGE, expectSuccess(), parameters).getClientSettings();
    }

    @Step("Получить настройки рассылки и ожидать ошибку {0}")
    public ClientSettings getClientSettingsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getClientSettings(ERROR_MESSAGE, expectError(error), parameters).getClientSettings();
    }

    private ManagementV1ClientSettingsGETSchema getClientSettings(String message, Matcher matcher,
                                                                 IFormParameters... parameters) {
        ManagementV1ClientSettingsGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/client/settings").get(parameters))
                .readResponse(ManagementV1ClientSettingsGETSchema.class);

        assertThat(message, result, matcher);
        return result;
    }

    @Step("Записать настройки рассылки {0}")
    public ClientSettings saveClientSettingsAndExpectSuccess(
            ClientSettingsObjectWrapper clientSettings, IFormParameters... parameters) {
        return saveClientSettings(SUCCESS_MESSAGE, expectSuccess(), clientSettings.get(), parameters);
    }

    @Step("Записать настройки рассылки {1} и ожидать ошибку {0}")
    public ClientSettings saveClientSettingsAndExpectError(IExpectedError error, ClientSettingsObjectWrapper clientSettings,
                                                           IFormParameters... parameters) {
        return saveClientSettings(ERROR_MESSAGE, expectError(error), clientSettings.get(), parameters);
    }

    private ClientSettings saveClientSettings(String message, Matcher matcher,
                                                                    ClientSettings clientSettings,
                                                                    IFormParameters... parameters) {
        ManagementV1ClientSettingsPOSTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/client/settings").post(
                        new ManagementV1ClientSettingsPOSTRequestSchema().withClientSettings(clientSettings),
                        parameters))
                .readResponse(ManagementV1ClientSettingsPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getClientSettings();
    }
}
