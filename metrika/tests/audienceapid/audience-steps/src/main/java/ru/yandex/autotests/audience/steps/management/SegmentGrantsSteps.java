package ru.yandex.autotests.audience.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdGrantDELETESchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdGrantPUTRequestSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdGrantPUTSchema;
import ru.yandex.autotests.audience.beans.schemes.V1ManagementSegmentSegmentIdGrantsGETSchema;
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
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 28.03.2017.
 */
public class SegmentGrantsSteps extends HttpClientLiteFacade {
    public SegmentGrantsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список разрешений для сегмента {0}")
    public List<Grant> getGrants(Long segmentId, IFormParameters... parameters) {
        return getGrants(SUCCESS_MESSAGE, expectSuccess(), segmentId, parameters).getGrants();
    }

    @Step("Получить список разрешений для сегмента {1} и ожидать ошибку {0}")
    public List<Grant> getGrantsAndExpectError(IExpectedError error, Long segmentId, IFormParameters... parameters) {
        return getGrants(ERROR_MESSAGE, expectError(error), segmentId, parameters).getGrants();
    }

    private V1ManagementSegmentSegmentIdGrantsGETSchema getGrants(String message, Matcher matcher, Long segmentId,
                                                                  IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdGrantsGETSchema result = get(V1ManagementSegmentSegmentIdGrantsGETSchema.class,
                format("/v1/management/segment/%s/grants", segmentId), parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать разрешение на сегмент {0}")
    public Grant createGrant(Long segmentId, Grant grant, IFormParameters... parameters) {
        return createGrant(SUCCESS_MESSAGE, expectSuccess(), segmentId, grant, parameters).getGrant();
    }

    @Step("Создать разрешение на сегмент {1} и ожидать ошибку {0}")
    public Grant createGrantAndExpectError(IExpectedError error, Long segmentId, Grant grant,
                                           IFormParameters... parameters) {
        return createGrant(ERROR_MESSAGE, expectError(error), segmentId, grant, parameters).getGrant();
    }

    private V1ManagementSegmentSegmentIdGrantPUTSchema createGrant(String message, Matcher matcher,
                                                                   Long segmentId, Grant grant,
                                                                   IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdGrantPUTSchema result = put(V1ManagementSegmentSegmentIdGrantPUTSchema.class,
                format("/v1/management/segment/%s/grant", segmentId),
                new V1ManagementSegmentSegmentIdGrantPUTRequestSchema().withGrant(grant),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить разрешение на сегмент {0} пользователя {1}")
    public Boolean deleteGrant(Long segmentId, String userLogin, IFormParameters... parameters) {
        return deleteGrant(SUCCESS_MESSAGE, expectSuccess(), segmentId, userLogin, parameters).getSuccess();
    }

    @Step("Удалить разрешение на сегмент {1} пользователя {2} и ожидать ошибку {0}")
    public Boolean deleteGrant(IExpectedError error, Long segmentId, String userLogin, IFormParameters... parameters) {
        return deleteGrant(ERROR_MESSAGE, expectError(error), segmentId, userLogin, parameters).getSuccess();
    }

    private V1ManagementSegmentSegmentIdGrantDELETESchema deleteGrant(String message, Matcher matcher,
                                                                      Long segmentId,
                                                                      String userLogin,
                                                                      IFormParameters... parameters) {
        V1ManagementSegmentSegmentIdGrantDELETESchema result = delete(V1ManagementSegmentSegmentIdGrantDELETESchema.class,
                format("/v1/management/segment/%s/grant", segmentId),
                makeParameters()
                        .append(userLogin(userLogin))
                        .append(parameters));

        assertThat(message, result, matcher);

        return result;
    }
}
