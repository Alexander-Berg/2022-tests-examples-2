package ru.yandex.autotests.audience.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementDelegateDELETESchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementDelegatePUTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementDelegatePUTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementDelegatesGETSchema;
import ru.yandex.autotests.audience.data.wrappers.DelegateWrapper;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.audience.pubapi.Delegate;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static ru.yandex.autotests.audience.parameters.UserLoginParameters.userLogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 28.03.2017.
 */
public class DelegatesSteps extends HttpClientLiteFacade {
    public DelegatesSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список представителей")
    public List<Delegate> getDelegates(IFormParameters... parameters) {
        return getDelegates(SUCCESS_MESSAGE, expectSuccess(), parameters).getDelegates();
    }

    @Step("Получить список представителей и ожидать ошибку {0}")
    public List<Delegate> getDelegatesAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getDelegates(ERROR_MESSAGE, expectError(error), parameters).getDelegates();
    }

    private V1ManagementDelegatesGETSchema getDelegates(String message, Matcher matcher, IFormParameters... parameters) {
        V1ManagementDelegatesGETSchema result = get(V1ManagementDelegatesGETSchema.class,
                "/v1/management/delegates", parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Добавить представителя {0}")
    public List<Delegate> createDelegate(DelegateWrapper delegateWrapper, IFormParameters... parameters) {
        return createDelegate(SUCCESS_MESSAGE, expectSuccess(), delegateWrapper.get(), parameters).getDelegates();
    }

    @Step("Добавить представителя {1} - и ожидать ошибку {0}")
    public List<Delegate> createDelegateAndExpectError(IExpectedError error, DelegateWrapper delegateWrapper,
                                                       IFormParameters... parameters) {
        return createDelegate(ERROR_MESSAGE, expectError(error), delegateWrapper.get(), parameters).getDelegates();
    }

    private V1ManagementDelegatePUTSchema createDelegate(String message, Matcher matcher,
                                                         Delegate delegate, IFormParameters... parameters) {
        V1ManagementDelegatePUTSchema result = put(V1ManagementDelegatePUTSchema.class,
                "/v1/management/delegate",
                new V1ManagementDelegatePUTRequestSchema().withDelegate(delegate),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить представителя {0}")
    public Boolean deleteDelegate(String userLogin, IFormParameters... parameters) {
        return deleteDelegate(SUCCESS_MESSAGE, expectSuccess(), userLogin, parameters).getSuccess();
    }

    @Step("Удалить представителя {1} и ожидать ошибку {0}")
    public Boolean deleteDelegateAndExpectError(IExpectedError error, String userLogin, IFormParameters... parameters) {
        return deleteDelegate(ERROR_MESSAGE, expectError(error), userLogin, parameters).getSuccess();
    }

    private V1ManagementDelegateDELETESchema deleteDelegate(String message, Matcher matcher, String userLogin,
                                                            IFormParameters... parameters) {
        V1ManagementDelegateDELETESchema result = delete(V1ManagementDelegateDELETESchema.class,
                "/v1/management/delegate",
                makeParameters()
                    .append(userLogin(userLogin))
                    .append(parameters));

        assertThat(message, result, matcher);

        return result;
    }
}
