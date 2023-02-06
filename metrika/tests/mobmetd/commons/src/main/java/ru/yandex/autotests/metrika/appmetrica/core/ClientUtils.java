package ru.yandex.autotests.metrika.appmetrica.core;

import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.entity.ContentType;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.HttpClientLiteParserException;
import ru.yandex.autotests.httpclientlite.core.RequestBuilder;
import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;

import java.net.URI;

import static java.nio.charset.StandardCharsets.UTF_8;
import static org.apache.commons.lang3.reflect.MethodUtils.invokeMethod;

public class ClientUtils {

    public static final String APPLICATION_ZIP = "application/zip";
    public static final String APPLICATION_ZIP_UTF_8 = ContentType.create(APPLICATION_ZIP, UTF_8).toString();

    /**
     * Этот метод добавляет параметр headers к {@link HttpClientLite#execute(RequestBuilder.Method, URI, Object, Class)}
     */
    public static <ResponseType> ResponseType execute(HttpClientLite client,
                                                      RequestBuilder.Method method,
                                                      URI uri,
                                                      FreeFormParameters headers,
                                                      Object body,
                                                      Class<ResponseType> responseTypeClass) {
        HttpUriRequest request = ((AppMetricaRequestBuilder) client.getRequestBuilder())
                .build(method, uri, headers, body);

        Response response = client.execute(request);
        return parseEntity(client, response, responseTypeClass);
    }

    public static Response execute(HttpClientLite client,
                                   RequestBuilder.Method method,
                                   URI uri,
                                   FreeFormParameters headers,
                                   Object body) {
        HttpUriRequest request = ((AppMetricaRequestBuilder) client.getRequestBuilder())
                .build(method, uri, headers, body);

        return client.execute(request);
    }

    /**
     * Этот метод делает вызов private метода {@link HttpClientLite#parseEntity(Response, Class)}
     */
    @SuppressWarnings("unchecked")
    public static <ResponseType> ResponseType parseEntity(HttpClientLite client,
                                                          Response response,
                                                          Class<ResponseType> responseTypeClass) {
        try {
            return (ResponseType) invokeMethod(client, true, "parseEntity", response, responseTypeClass);
        } catch (Exception e) {
            throw new HttpClientLiteParserException("error while parsing response to pointed type", e);
        }
    }
}
