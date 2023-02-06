package ru.yandex.autotests.audience.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementAccountsGETSchema;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.Account;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 28.03.2017.
 */
public class AccountsSteps extends HttpClientLiteFacade {
    public AccountsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список аккаунтов")
    public List<Account> getAccounts(IFormParameters... parameters) {
        return getAccounts(SUCCESS_MESSAGE, expectSuccess(), parameters).getAccounts();
    }

    @Step("Получить список аккаунтов и ожидать ошибку {0}")
    public List<Account> getAccountsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getAccounts(ERROR_MESSAGE, expectError(error), parameters).getAccounts();
    }

    private V1ManagementAccountsGETSchema getAccounts(String message, Matcher matcher, IFormParameters... parameters) {
        V1ManagementAccountsGETSchema result = get(V1ManagementAccountsGETSchema.class,
                "/v1/management/accounts", parameters);

        assertThat(message, result, matcher);

        return result;
    }
}
