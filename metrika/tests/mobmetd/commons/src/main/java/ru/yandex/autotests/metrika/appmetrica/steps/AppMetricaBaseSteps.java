package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableSet;
import org.apache.http.client.utils.URIBuilder;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.core.RequestBuilder;
import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.metrika.appmetrica.core.ClientUtils;
import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;

import static org.hamcrest.Matchers.any;
import static org.hamcrest.Matchers.anyOf;
import static ru.yandex.autotests.httpclientlite.core.RequestBuilder.Method.DELETE;
import static ru.yandex.autotests.httpclientlite.core.RequestBuilder.Method.GET;
import static ru.yandex.autotests.httpclientlite.core.RequestBuilder.Method.POST;
import static ru.yandex.autotests.httpclientlite.core.RequestBuilder.Method.PUT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Степы представляют собой удобную абстракцию на вызовами rest методов конкретных контроллеров.
 * В данном классе собраны общие методы для написания такой функциональности.
 */
public abstract class AppMetricaBaseSteps {

    private static final int QUERY_TOO_COMPLICATED_RETRIES = 2;

    private final URL baseUrl;
    private final HttpClientLite client;

    public AppMetricaBaseSteps(URL baseUrl, HttpClientLite client) {
        this.baseUrl = baseUrl;
        this.client = client;
    }

    protected <ResponseType> ResponseType get(Class<ResponseType> responseTypeClass,
                                              String path,
                                              IFormParameters... parameters) {
        return executeWithRetryOnQueryTooComplicated(responseTypeClass, GET, path, makeParameters(), null, parameters);
    }

    protected <ResponseType> ResponseType post(Class<ResponseType> responseTypeClass,
                                               String path,
                                               IFormParameters... parameters) {
        return post(responseTypeClass, path, makeParameters(), null, parameters);
    }

    protected <ResponseType> ResponseType post(Class<ResponseType> responseTypeClass,
                                               String path,
                                               Object body,
                                               IFormParameters... parameters) {
        return post(responseTypeClass, path, makeParameters(), body, parameters);
    }

    protected <ResponseType> ResponseType post(Class<ResponseType> responseTypeClass,
                                               String path,
                                               FreeFormParameters headers,
                                               Object body,
                                               IFormParameters... parameters) {
        return execute(responseTypeClass, POST, path, headers, body, parameters);
    }

    protected <ResponseType> ResponseType put(Class<ResponseType> responseTypeClass,
                                              String path,
                                              Object body,
                                              IFormParameters... parameters) {
        return put(responseTypeClass, path, makeParameters(), body, parameters);
    }

    protected <ResponseType> ResponseType put(Class<ResponseType> responseTypeClass,
                                              String path,
                                              IFormParameters... parameters) {
        return put(responseTypeClass, path, makeParameters(), null, parameters);
    }

    protected <ResponseType> ResponseType put(Class<ResponseType> responseTypeClass,
                                              String path,
                                              FreeFormParameters headers,
                                              Object body,
                                              IFormParameters... parameters) {
        return execute(responseTypeClass, PUT, path, headers, body, parameters);
    }

    protected <ResponseType> ResponseType delete(Class<ResponseType> responseTypeClass,
                                                 String path,
                                                 IFormParameters... parameters) {
        return execute(responseTypeClass, DELETE, path, makeParameters(), null, parameters);
    }

    private <ResponseType> ResponseType executeWithRetryOnQueryTooComplicated(Class<ResponseType> responseTypeClass,
                                                                              RequestBuilder.Method method,
                                                                              String path,
                                                                              FreeFormParameters headers,
                                                                              Object body,
                                                                              IFormParameters... parameters) {
        ResponseType response = execute(responseTypeClass, method, path, headers, body, parameters);
        for (int i = 0; i < QUERY_TOO_COMPLICATED_RETRIES && failedOnTooComplicatedQuery(response); ++i) {
            response = execute(responseTypeClass, method, path, headers, body, parameters);
        }
        return response;
    }

    protected <ResponseType> ResponseType execute(Class<ResponseType> responseTypeClass,
                                                  RequestBuilder.Method method,
                                                  String path,
                                                  FreeFormParameters headers,
                                                  Object body,
                                                  IFormParameters... parameters) {
        if (apiProperties().isCheckEmptyBodyRequests() && body != null && ImmutableSet.of(POST, PUT).contains(method)) {
            checkEmptyBodyRequest(responseTypeClass, method, path, headers, parameters);
        }
        URI uri = buildUri(path, parameters);
        return ClientUtils.execute(client, method, uri, headers, body, responseTypeClass);
    }

    protected Response execute(RequestBuilder.Method method,
                               String path,
                               FreeFormParameters headers,
                               Object body,
                               IFormParameters... parameters) {
        URI uri = buildUri(path, parameters);
        return ClientUtils.execute(client, method, uri, headers, body);
    }

    private URI buildUri(String path, IFormParameters... parameters) {
        try {
            URIBuilder uriBuilder = new URIBuilder(baseUrl.toURI());
            uriBuilder.setPath(uriBuilder.getPath() + "/" + path);
            if (parameters != null) {
                for (IFormParameters p : parameters) {
                    if (p != null) {
                        uriBuilder.addParameters(p.getParameters());
                    }
                }
            }
            return uriBuilder.build();
        } catch (URISyntaxException e) {
            throw new AppMetricaException("Ошибка при формировании URI запроса", e);
        }
    }

    private <ResponseType> void checkEmptyBodyRequest(Class<ResponseType> responseTypeClass,
                                                      RequestBuilder.Method method,
                                                      String path,
                                                      FreeFormParameters headers,
                                                      IFormParameters... parameters) {
        Object emptyBody = new Object();
        ResponseType emptyBodyResponse = execute(responseTypeClass, method, path, headers, emptyBody, parameters);
        assumeThat("Запрос с пустым телом не приводит к 5хх", emptyBodyResponse, anyOf(
                expectSuccess(),
                expectError(400L, any(String.class)),
                expectError(403L, any(String.class)),
                expectError(404L, any(String.class))));

    }

    private static boolean failedOnTooComplicatedQuery(Object response) {
        JsonNode responseJson = new ObjectMapper().valueToTree(response);
        if (!responseJson.has("message")) {
            return false;
        }
        JsonNode messageNode = responseJson.get("message");
        if (!messageNode.isTextual()) {
            return false;
        }
        String message = messageNode.asText();
        return message.contains("Запрос слишком сложный.") || message.contains("Query is too complicated.");
    }
}
