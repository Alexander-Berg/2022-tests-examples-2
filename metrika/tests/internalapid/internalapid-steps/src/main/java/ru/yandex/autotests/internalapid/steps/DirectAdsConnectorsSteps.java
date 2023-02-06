package ru.yandex.autotests.internalapid.steps;

import java.net.URL;
import java.util.List;

import org.hamcrest.Matcher;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesConnectorsPlatformCounterIdCreateTestConnectorPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesConnectorsPlatformListGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesCounterCounterIdConnectorConnectorIdDELETESchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesCounterCounterIdConnectorConnectorIdGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesCounterCounterIdConnectorConnectorIdPUTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesCounterCounterIdConnectorConnectorIdPUTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesCounterCounterIdConnectorPOSTRequestSchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesCounterCounterIdConnectorPOSTSchema;
import ru.yandex.autotests.internalapid.beans.schemes.ExpensesCounterCounterIdConnectorsGETSchema;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class DirectAdsConnectorsSteps extends HttpClientLiteFacade {

    private final static DateTimeFormatter FORMAT = DateTimeFormat.forPattern("yyyy-MM-dd");

    public DirectAdsConnectorsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

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
        ExpensesConnectorsPlatformCounterIdCreateTestConnectorPOSTSchema result = post(
                ExpensesConnectorsPlatformCounterIdCreateTestConnectorPOSTSchema.class,
                format("/expenses/connectors/%s/%s/create_test_connector", "google", counterId),
                new Object(),
                parameters
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getConnector();
    }

    private boolean deleteConnector(String message, Matcher matcher, long counterId, long connectorId, IFormParameters... parameters) {
        ExpensesCounterCounterIdConnectorConnectorIdDELETESchema result = delete(
                ExpensesCounterCounterIdConnectorConnectorIdDELETESchema.class,
                format("/expenses/counter/%s/connector/%s", counterId, connectorId),
                parameters);

        assertThat(message, result, matcher);

        return result.getSuccess() != null && result.getSuccess();
    }

    private AdsConnector updateConnector(String message, Matcher matcher, long counterId, long connectorId, AdsConnector update, IFormParameters... parameters) {
        ExpensesCounterCounterIdConnectorConnectorIdPUTRequestSchema body = new ExpensesCounterCounterIdConnectorConnectorIdPUTRequestSchema()
                .withAuthorized(update.getAuthorized())
                .withCabinets(update.getCabinets())
                .withConnectorId(update.getConnectorId())
                .withLogin(update.getLogin())
                .withName(update.getName())
                .withPlatform(update.getPlatform())
                .withUid(update.getUid());
        ExpensesCounterCounterIdConnectorConnectorIdPUTSchema result = put(
                ExpensesCounterCounterIdConnectorConnectorIdPUTSchema.class,
                format("/expenses/counter/%s/connector/%s", counterId, connectorId),
                body,
                parameters
        );

        assertThat(message, result, matcher);

        return result.getConnector();
    }

    private AdsConnector createConnector(String message, Matcher matcher, long counterId, AdsConnector source, IFormParameters... parameters) {
        ExpensesCounterCounterIdConnectorPOSTRequestSchema body = new ExpensesCounterCounterIdConnectorPOSTRequestSchema()
                .withAuthorized(source.getAuthorized())
                .withCabinets(source.getCabinets())
                .withConnectorId(source.getConnectorId())
                .withLogin(source.getLogin())
                .withName(source.getName())
                .withPlatform(source.getPlatform())
                .withUid(source.getUid());

        ExpensesCounterCounterIdConnectorPOSTSchema result = post(
                ExpensesCounterCounterIdConnectorPOSTSchema.class,
                format("/expenses/counter/%s/connector", counterId),
                body,
                parameters
        );

        assertThat(message, result, matcher);

        return result.getConnector();
    }

    private AdsConnector getConnector(String message, Matcher matcher, long counterId, long connectorId, IFormParameters... parameters) {
        ExpensesCounterCounterIdConnectorConnectorIdGETSchema result = get(
                ExpensesCounterCounterIdConnectorConnectorIdGETSchema.class,
                format("/expenses/counter/%s/connector/%s", counterId, connectorId),
                parameters
        );

        assertThat(message, result, matcher);

        return result.getConnector();
    }

    private List<AdsConnector> getConnectorsByCounter(String message, Matcher matcher, long counterId, String platform, String filter, IFormParameters... parameters) {
        ExpensesCounterCounterIdConnectorsGETSchema result = get(
                ExpensesCounterCounterIdConnectorsGETSchema.class,
                format("/expenses/counter/%s/connectors", counterId),
                makeParameters().append("platform", platform).append("filter", filter).append(parameters)
        );

        assertThat(message, result, matcher);

        return result.getConnectors();
    }

    private List<AdsConnector> listConnectors(String message, Matcher matcher, String platform, IFormParameters... parameters) {
        ExpensesConnectorsPlatformListGETSchema result = get(
                ExpensesConnectorsPlatformListGETSchema.class,
                format("/expenses/connectors/%s/list", platform),
                parameters
        );

        assertThat(message, result, matcher);

        return result.getConnectors();
    }

}
