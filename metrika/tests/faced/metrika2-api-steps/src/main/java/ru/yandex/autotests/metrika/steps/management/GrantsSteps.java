package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.core.MetrikaRequestBuilder;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 05.03.2015.
 */
public class GrantsSteps extends MetrikaBaseSteps {

    @Step("Получить список разрешений для счетчика {0}")
    public List<GrantE> getGrantsAndExpectSuccess(Long counterId) {
        return getGrants(SUCCESS_MESSAGE, expectSuccess(), counterId);
    }

    @Step("Получить список разрешений для счетчика {1} и ожидать ошибку {0}")
    public void getGrantsAndExpectError(IExpectedError error, Long counterId) {
        getGrants(ERROR_MESSAGE, expectError(error), counterId);
    }

    private List<GrantE> getGrants(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdGrantsGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grants", counterId)).get())
                .readResponse(ManagementV1CounterCounterIdGrantsGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result.getGrants();
    }

    @Step("Изменить разрешение для счетчика {0}")
    public GrantE editGrantAndExpectSuccess(Long counterId, GrantE grant) {
        return editGrant(SUCCESS_MESSAGE, expectSuccess(), counterId, grant);
    }

    @Step("Изменить разрешение для счетчика {1} и ожидать ошибку {0}")
    public void editGrantAndExpectError(IExpectedError error, Long counterId, GrantE grant) {
        editGrant(ERROR_MESSAGE, expectError(error), counterId, grant);
    }

    private GrantE editGrant(String message, Matcher matcher, Long counterId,
                             GrantE grant) {
        ManagementV1CounterCounterIdGrantPUTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grant", counterId))
                        .put(new ManagementV1CounterCounterIdGrantPUTRequestSchema().withGrant(grant)))
                .readResponse(ManagementV1CounterCounterIdGrantPUTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result.getGrant();
    }

    @Step("Удалить разрешение для пользователя {1} на счетчик {0} и ожидать успешного заверешния запроса")
    public void deleteGrantAndExpectSuccess(Long counterId, String login) {
        deleteUserGrant(SUCCESS_MESSAGE, expectSuccess(), counterId, login);
    }

    @Step("Удалить разрешение для пользователя {2} на счетчик {1} и ожидать ошибку {0}")
    public void deleteGrantAndExpectError(IExpectedError error, Long counterId, String login) {
        deleteUserGrant(ERROR_MESSAGE, expectError(error), counterId, login);
    }

    private void deleteUserGrant(String message, Matcher matcher, Long counterId, String login) {
        ManagementV1CounterCounterIdGrantDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grant", counterId))
                        .delete(makeParameters("user_login", login)))
                .readResponse(ManagementV1CounterCounterIdGrantDELETESchema.class);

        TestSteps.assertThat(message, result, matcher);
    }

    @Step("Удалить публичный доступ и ожидать успешного заверешния запроса")
    public void deletePublicGrantAndExpectSuccess(Long counterId) {
        deletePublicGrant(SUCCESS_MESSAGE, expectSuccess(), counterId);
    }

    @Step("Удалить публичный доступ и ожидать ошибку {0}")
    public void deletePublicGrantAndExpectError(IExpectedError error, Long counterId) {
        deletePublicGrant(ERROR_MESSAGE, expectError(error), counterId);
    }

    private void deletePublicGrant(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdGrantDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/public_grant", counterId))
                        .delete(makeParameters()))
                .readResponse(ManagementV1CounterCounterIdGrantDELETESchema.class);

        TestSteps.assertThat(message, result, matcher);
    }

    @Step("Получить информацию о разрешении для пользователя {1} на счетчик {0} и ожидать успешного заверешния запроса")
    public GrantE getGrantAndExpectSuccess(Long counterId, String login) {
        return getGrant(SUCCESS_MESSAGE, expectSuccess(), counterId, login);
    }

    @Step("Получить информацию о разрешении для пользователя {2} на счетчик {1} и ожидать ошибку {0}")
    public void getGrantAndExpectError(IExpectedError error, Long counterId, String login) {
        getGrant(ERROR_MESSAGE, expectError(error), counterId, login);
    }

    private GrantE getGrant(String message, Matcher matcher, Long counterId, String login) {
        ManagementV1CounterCounterIdGrantGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grant", counterId))
                        .get(makeParameters("user_login", login)))
                .readResponse(ManagementV1CounterCounterIdGrantGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result.getGrant();
    }

    @Step("Создать разрешение для счетчика {0}")
    public GrantE setGrantAndExpectSuccess(Long counterId, GrantE grant, IFormParameters... parameters) {
        return setGrant(SUCCESS_MESSAGE, expectSuccess(), counterId, grant, parameters);
    }

    @Step("Создать разрешения для счетчика {0}")
    public void setGrantsAndExpectSuccess(Long counterId, List<GrantE> grants, IFormParameters... parameters) {
        grants.forEach(grant -> setGrant(SUCCESS_MESSAGE, expectSuccess(), counterId, grant, parameters));
    }

    @Step("Создать разрешение для счетчика {1} и ожидать ошибку {0}")
    public void setGrantAndExpectError(IExpectedError error, Long counterId, GrantE grant, IFormParameters... parameters) {
        setGrant(ERROR_MESSAGE, expectError(error), counterId, grant, parameters);
    }

    private GrantE setGrant(String message, Matcher matcher, Long counterId, GrantE grant, IFormParameters... parameters) {
        if(grant.getPerm().equals(GrantType.PUBLIC_STAT)) {
            return setPublicGrant(message, matcher, counterId, parameters);
        } else {
            return setUserGrant(message, matcher, counterId, grant, parameters);
        }
    }

    private GrantE setUserGrant(String message, Matcher matcher, Long counterId, GrantE grant,
            IFormParameters[] parameters)
    {
        MetrikaRequestBuilder requestBuilder =
                getRequestBuilder(String.format("/management/v1/counter/%s/grants", counterId));

        ManagementV1CounterCounterIdGrantsPOSTSchema result = executeAsJson(
                requestBuilder.post(new ManagementV1CounterCounterIdGrantsPOSTRequestSchema().withGrant(grant),
                        parameters))
                .readResponse(ManagementV1CounterCounterIdGrantsPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result.getGrant();
    }

    private GrantE setPublicGrant(String message, Matcher matcher, Long counterId, IFormParameters... parameters) {
        MetrikaRequestBuilder requestBuilder = getRequestBuilder(String.format("/management/v1/counter/%s/public_grant", counterId));

        ManagementV1CounterCounterIdGrantsPOSTSchema result = executeAsJson(
                requestBuilder.post(parameters))
                .readResponse(ManagementV1CounterCounterIdGrantsPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result.getGrant();
    }

}
