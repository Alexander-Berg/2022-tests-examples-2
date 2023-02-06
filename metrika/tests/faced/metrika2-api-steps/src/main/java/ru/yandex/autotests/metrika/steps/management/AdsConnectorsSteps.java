package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

public class AdsConnectorsSteps extends MetrikaBaseSteps {

    @Step("Получить список активных подключений")
    public List<AdsConnector> listConnectorsAndExpectSuccess(String platform, IFormParameters... parameters) {
        return listConnectors(SUCCESS_MESSAGE, expectSuccess(), platform, parameters);
    }

    @Step("Получить список активных подключений и ожидать ошибку {1}")
    public List<AdsConnector> listConnectorsAndExpectError(String platform, IExpectedError error, IFormParameters... parameters) {
        return listConnectors(ERROR_MESSAGE, expectError(error), platform, parameters);
    }

    @Step("Получить список активных подключений для счтечика {0}")
    public List<AdsConnector> getConnectorsByCounterAndExpectSuccess(long counterId, String platform, String filter, IFormParameters... parameters) {
        return getConnectorsByCounter(SUCCESS_MESSAGE, expectSuccess(), counterId, platform, filter, parameters);
    }

    @Step("Получить список активных подключений для счтечика {0} и ожидать ошибку {3}")
    public List<AdsConnector> getConnectorsByCounterAndExpectError(long counterId, String platform, String filter, IExpectedError error, IFormParameters... parameters) {
        return getConnectorsByCounter(ERROR_MESSAGE, expectError(error), counterId, platform, filter, parameters);
    }

    @Step("Получить подключение {1} для счетчика {0}")
    public AdsConnector getConnectorAndExpectSuccess(long counterId, long connectorId, IFormParameters... parameters) {
        return getConnector(SUCCESS_MESSAGE, expectSuccess(), counterId, connectorId, parameters);
    }

    @Step("Получить подключение {1} для счетчика {0} и ожидать ошибку {2}")
    public AdsConnector getConnectorAndExpectError(long counterId, long connectorId, IExpectedError error, IFormParameters... parameters) {
        return getConnector(ERROR_MESSAGE, expectError(error), counterId, connectorId, parameters);
    }

    @Step("Создать подключение для счетчика {0}")
    public AdsConnector createConnectorAndExpectSuccess(long counterId, AdsConnector source, IFormParameters... parameters) {
        return createConnector(SUCCESS_MESSAGE, expectSuccess(), counterId, source, parameters);
    }

    @Step("Создать подключение для счетчика {0} и ожидать ошибку {2}")
    public AdsConnector createConnectorAndExpectError(long counterId, AdsConnector source, IExpectedError error, IFormParameters... parameters) {
        return createConnector(ERROR_MESSAGE, expectError(error), counterId, source, parameters);
    }

    @Step("Изменить подключение {1} для счетчика {0}")
    public AdsConnector updateConnectorAndExpectSuccess(long counterId, long connectorId, AdsConnector update, IFormParameters... parameters) {
        return updateConnector(SUCCESS_MESSAGE, expectSuccess(), counterId, connectorId, update, parameters);
    }

    @Step("Изменить подключение {1} для счетчика {0} и ожидать ошибку {3}")
    public AdsConnector updateConnectorAndExpectError(long counterId, long connectorId, AdsConnector update, IExpectedError error, IFormParameters... parameters) {
        return updateConnector(ERROR_MESSAGE, expectError(error), counterId, connectorId, update, parameters);
    }

    @Step("Удалить подключение {1} для счетчика {0}")
    public boolean deleteConnectorAndExpectSuccess(long counterId, long connectorId, IFormParameters... parameters) {
        return deleteConnector(SUCCESS_MESSAGE, expectSuccess(), counterId, connectorId, parameters);
    }

    @Step("Удалить подключение {1} для счетчика {0} и ожидать ошибку {2}")
    public boolean deleteConnectorAndExpectError(long counterId, long connectorId, IExpectedError error, IFormParameters... parameters) {
        return deleteConnector(ERROR_MESSAGE, expectError(error), counterId, connectorId, parameters);
    }

    @Step("Создать новое подключение без авторизации для счетчика {0}")
    public AdsConnector createConnectorWithoutAuthorizationAndExpectSuccess(long counterId, IFormParameters... parameters) {
        InternalConnectorsPlatformCounterIdCreateTestConnectorPOSTSchema result = executeAsJson(
                getRequestBuilder(format("/internal/connectors/%s/%s/create_test_connector", "google", counterId)).post(parameters))
                .readResponse(InternalConnectorsPlatformCounterIdCreateTestConnectorPOSTSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getConnector();
    }

    private boolean deleteConnector(String message, Matcher matcher, long counterId, long connectorId, IFormParameters... parameters) {
        InternalCounterCounterIdConnectorConnectorIdDELETESchema result = executeAsJson(
                getRequestBuilder(format("/internal/counter/%s/connector/%s", counterId, connectorId)).delete(parameters))
                .readResponse(InternalCounterCounterIdConnectorConnectorIdDELETESchema.class);

        assertThat(message, result, matcher);

        return result.getSuccess() != null && result.getSuccess();
    }

    private AdsConnector updateConnector(String message, Matcher matcher, long counterId, long connectorId, AdsConnector update, IFormParameters... parameters) {
        InternalCounterCounterIdConnectorConnectorIdPUTRequestSchema body = new InternalCounterCounterIdConnectorConnectorIdPUTRequestSchema()
                .withAuthorized(update.getAuthorized())
                .withCabinets(update.getCabinets())
                .withConnectorId(update.getConnectorId())
                .withLogin(update.getLogin())
                .withName(update.getName())
                .withPlatform(update.getPlatform())
                .withUid(update.getUid());

        InternalCounterCounterIdConnectorConnectorIdPUTSchema result = executeAsJson(
                getRequestBuilder(format("/internal/counter/%s/connector/%s", counterId, connectorId)).put(body, parameters))
                .readResponse(InternalCounterCounterIdConnectorConnectorIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result.getConnector();
    }

    private AdsConnector createConnector(String message, Matcher matcher, long counterId, AdsConnector source, IFormParameters... parameters) {
        InternalCounterCounterIdConnectorPOSTRequestSchema body = new InternalCounterCounterIdConnectorPOSTRequestSchema()
                .withAuthorized(source.getAuthorized())
                .withCabinets(source.getCabinets())
                .withConnectorId(source.getConnectorId())
                .withLogin(source.getLogin())
                .withName(source.getName())
                .withPlatform(source.getPlatform())
                .withUid(source.getUid());

        InternalCounterCounterIdConnectorPOSTSchema result = executeAsJson(
                getRequestBuilder(format("/internal/counter/%s/connector", counterId)).post(body, parameters))
                .readResponse(InternalCounterCounterIdConnectorPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getConnector();
    }

    private AdsConnector getConnector(String message, Matcher matcher, long counterId, long connectorId, IFormParameters... parameters) {
        InternalCounterCounterIdConnectorConnectorIdGETSchema result = executeAsJson(
                getRequestBuilder(format("/internal/counter/%s/connector/%s", counterId, connectorId)).get(parameters))
                .readResponse(InternalCounterCounterIdConnectorConnectorIdGETSchema.class);

        assertThat(message, result, matcher);

        return result.getConnector();
    }

    private List<AdsConnector> getConnectorsByCounter(String message, Matcher matcher, long counterId, String platform, String filter, IFormParameters... parameters) {
        InternalCounterCounterIdConnectorsGETSchema result = executeAsJson(
                getRequestBuilder(format("/internal/counter/%s/connectors", counterId)).get(
                        makeParameters().append("platform", platform).append("filter", filter).append(parameters)
                ))
                .readResponse(InternalCounterCounterIdConnectorsGETSchema.class);

        assertThat(message, result, matcher);

        return result.getConnectors();
    }

    private List<AdsConnector> listConnectors(String message, Matcher matcher, String platform, IFormParameters... parameters) {
        InternalConnectorsPlatformListGETSchema result = executeAsJson(
                getRequestBuilder(format("/internal/connectors/%s/list", platform)).get(parameters))
                .readResponse(InternalConnectorsPlatformListGETSchema.class);

        assertThat(message, result, matcher);

        return result.getConnectors();
    }
}
