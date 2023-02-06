package ru.yandex.autotests.advapi.steps.management;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import java.net.URL;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;

public class BaseAdvApiSteps extends HttpClientLiteFacade {

    public BaseAdvApiSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    protected <T> T deleteAndExpectSuccess(Class<T> responseTypeClass, String path, IFormParameters... parameters) {
        T response = delete(responseTypeClass, path, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());

        return response;
    }

    protected <T> T deleteAndExpectError(Class<T> responseTypeClass, String path, IExpectedError error, IFormParameters... parameters) {
        T response = delete(responseTypeClass, path, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(ERROR_MESSAGE, response, expectError(error));

        return response;
    }

    protected <T> T putAndExpectSuccess(Class<T> responseTypeClass, String path, Object body, IFormParameters... parameters) {
        T response = put(responseTypeClass, path, body, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());

        return response;
    }

    protected <T> T putAndExpectError(Class<T> responseTypeClass, String path, Object body, IExpectedError error, IFormParameters... parameters) {
        T response = put(responseTypeClass, path, body, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(ERROR_MESSAGE, response, expectError(error));

        return response;
    }

    protected <T> T postAndExpectSuccess(Class<T> responseTypeClass, String path, Object body, IFormParameters... parameters) {
        T response = post(responseTypeClass, path, body, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());

        return response;
    }

    protected <T> T postAndExpectError(Class<T> responseTypeClass, String path, Object body, IExpectedError error, IFormParameters... parameters) {
        T response = post(responseTypeClass, path, body, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(ERROR_MESSAGE, response, expectError(error));

        return response;
    }

    protected <T> T getAndExpectSuccess(Class<T> responseTypeClass, String path, IFormParameters... parameters) {
        T response = get(responseTypeClass, path, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());

        return response;
    }

    protected <T> T getAndExpectError(Class<T> responseTypeClass, String path, IExpectedError error, IFormParameters... parameters) {
        T response = get(responseTypeClass, path, parameters);

        //noinspection unchecked
        TestSteps.assumeThat(ERROR_MESSAGE, response, expectError(error));

        return response;
    }
}
