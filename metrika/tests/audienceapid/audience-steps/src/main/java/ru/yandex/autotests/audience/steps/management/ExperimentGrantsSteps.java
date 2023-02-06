package ru.yandex.autotests.audience.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementExperimentExperimentIdGrantDELETESchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementExperimentExperimentIdGrantPUTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementExperimentExperimentIdGrantPUTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementExperimentExperimentIdGrantsGETSchema;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.audience.parameters.UserLoginParameters.userLogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by konkov on 28.03.2017.
 */
public class ExperimentGrantsSteps extends HttpClientLiteFacade {
    public ExperimentGrantsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список разрешений для эксперимента {0}")
    public List<Grant> getGrants(Long experimentId, IFormParameters... parameters) {
        return getGrants(SUCCESS_MESSAGE, expectSuccess(), experimentId, parameters).getGrants();
    }

    @Step("Получить список разрешений для эксперимента {1} и ожидать ошибку {0}")
    public List<Grant> getGrantsAndExpectError(IExpectedError error, Long experimentId, IFormParameters... parameters) {
        return getGrants(ERROR_MESSAGE, expectError(error), experimentId, parameters).getGrants();
    }

    private V1ManagementExperimentExperimentIdGrantsGETSchema getGrants(String message, Matcher matcher, Long experimentId,
                                                                  IFormParameters... parameters) {
        V1ManagementExperimentExperimentIdGrantsGETSchema result = get(V1ManagementExperimentExperimentIdGrantsGETSchema.class,
                format("/v1/management/experiment/%s/grants", experimentId), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать разрешение на эксперимент {0}")
    public Grant createGrant(Long experimentId, Grant grant, IFormParameters... parameters) {
        return createGrant(SUCCESS_MESSAGE, expectSuccess(), experimentId, grant, parameters).getGrant();
    }

    @Step("Создать разрешение на эксперимент {1} и ожидать ошибку {0}")
    public Grant createGrantAndExpectError(IExpectedError error, Long experimentId, Grant grant,
                                           IFormParameters... parameters) {
        return createGrant(ERROR_MESSAGE, expectError(error), experimentId, grant, parameters).getGrant();
    }

    private V1ManagementExperimentExperimentIdGrantPUTSchema createGrant(String message, Matcher matcher,
                                                                   Long experimentId, Grant grant,
                                                                   IFormParameters... parameters) {
        V1ManagementExperimentExperimentIdGrantPUTSchema result = put(V1ManagementExperimentExperimentIdGrantPUTSchema.class,
                format("/v1/management/experiment/%s/grant", experimentId),
                new V1ManagementExperimentExperimentIdGrantPUTRequestSchema().withGrant(grant),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить разрешение на эксперимент {0} пользователя {1}")
    public Boolean deleteGrant(Long experimentId, String userLogin, IFormParameters... parameters) {
        return deleteGrant(SUCCESS_MESSAGE, expectSuccess(), experimentId, userLogin, parameters).getSuccess();
    }

    @Step("Удалить разрешение на эксперимент {1} пользователя {2} и ожидать ошибку {0}")
    public Boolean deleteGrant(IExpectedError error, Long experimentId, String userLogin, IFormParameters... parameters) {
        return deleteGrant(ERROR_MESSAGE, expectError(error), experimentId, userLogin, parameters).getSuccess();
    }

    private V1ManagementExperimentExperimentIdGrantDELETESchema deleteGrant(String message, Matcher matcher,
                                                                      Long experimentId,
                                                                      String userLogin,
                                                                      IFormParameters... parameters) {
        V1ManagementExperimentExperimentIdGrantDELETESchema result = delete(V1ManagementExperimentExperimentIdGrantDELETESchema.class,
                format("/v1/management/experiment/%s/grant", experimentId),
                makeParameters()
                        .append(userLogin(userLogin))
                        .append(parameters));

        assertThat(message, result, matcher);

        return result;
    }
}
