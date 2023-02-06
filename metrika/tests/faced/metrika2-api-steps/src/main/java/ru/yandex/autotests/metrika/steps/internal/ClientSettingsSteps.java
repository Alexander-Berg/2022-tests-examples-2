package ru.yandex.autotests.metrika.steps.internal;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.ClientSettingsObjectWrapper;
import ru.yandex.autotests.metrika.beans.schemes.InternalAdminClientsettingsUidPOSTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalAdminClientsettingsUidPOSTSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.ClientSettings;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by omatikaya on 21.02.17.
 */
public class ClientSettingsSteps extends MetrikaBaseSteps {
    @Step("Перезаписать настройки рассылки {0} для пользователя {1}")
    public ClientSettings rewriteClientSettingsAndExpectSuccess(
            ClientSettingsObjectWrapper clientSettings, long uid, IFormParameters... parameters) {
        return rewriteClientSettings(SUCCESS_MESSAGE, expectSuccess(), clientSettings.get(), uid, parameters);
    }

    @Step("Перезаписать настройки рассылки {1} для uid {2} и ожидать ошибку {0}")
    public ClientSettings rewriteClientSettingsAndExpectError(IExpectedError error,
            ClientSettingsObjectWrapper clientSettings, long uid, IFormParameters... parameters) {
        return rewriteClientSettings(ERROR_MESSAGE, expectError(error), clientSettings.get(), uid, parameters);
    }

    private ClientSettings rewriteClientSettings(String message, Matcher matcher,
                                                 ClientSettings clientSettings,
                                                 long uid,
                                                 IFormParameters... parameters) {
        InternalAdminClientsettingsUidPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/internal/admin/clientsettings/%s", uid)).post(
                        new InternalAdminClientsettingsUidPOSTRequestSchema().withClientSettings(clientSettings),
                        parameters))
                .readResponse(InternalAdminClientsettingsUidPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getClientSettings();
    }
}
