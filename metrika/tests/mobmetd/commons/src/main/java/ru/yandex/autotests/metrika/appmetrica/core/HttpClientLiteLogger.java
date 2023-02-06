package ru.yandex.autotests.metrika.appmetrica.core;

import org.apache.commons.io.output.WriterOutputStream;
import org.apache.http.Header;
import org.apache.http.HttpEntityEnclosingRequest;
import org.apache.http.client.methods.HttpUriRequest;
import org.slf4j.LoggerFactory;
import ru.yandex.autotests.httpclientlite.core.Logger;
import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.irt.testutils.allure.AllureUtils;

import java.io.IOException;
import java.io.OutputStream;
import java.io.StringWriter;
import java.net.URLDecoder;
import java.util.List;
import java.util.stream.Stream;

import static java.lang.String.format;
import static java.lang.System.lineSeparator;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.joining;
import static org.apache.commons.lang.StringUtils.EMPTY;
import static ru.yandex.autotests.metrika.commons.lambda.LambdaExceptionUtil.rethrowFunction;

public class HttpClientLiteLogger implements Logger {

    private org.slf4j.Logger log = LoggerFactory.getLogger(this.getClass());

    @Override
    public void logRequest(HttpUriRequest request) {
        String message = requestToString(request);
        log.info(message);
        AllureUtils.addTextAttachment("Запрос", message);
    }

    @Override
    public void logResponse(Response response) {
        String message = responseToString(response);
        log.info(message);
        AllureUtils.addTextAttachment("Ответ", message);
    }

    private String responseToString(Response response) {
        return new StringBuilder()
                .append(response.getStatusLine()).append(lineSeparator())
                .append(headersToString(response.getHeaders())).append(lineSeparator())
                .append(response.getResponseContent().toString())
                .toString();
    }

    private String requestToString(HttpUriRequest request) {
        return new StringBuilder()
                .append(request.getRequestLine()).append(lineSeparator())
                .append(queryToString(request.getURI().getRawQuery())).append(lineSeparator())
                .append(headersToString(asList(request.getAllHeaders())))
                .append(tryGetEntityContent(request))
                .toString();
    }

    private String queryToString(String rawQuery) {
        return Stream.of(rawQuery.split("&"))
                .map(rethrowFunction(f -> URLDecoder.decode(f, "UTF-8")))
                .collect(joining(lineSeparator()));
    }

    private String headersToString(List<Header> headers) {
        return headers.stream()
                .map(h -> format("%s: %s", h.getName(), h.getValue()))
                .collect(joining(lineSeparator()));
    }

    private static String tryGetEntityContent(HttpUriRequest request) {
        if (request instanceof HttpEntityEnclosingRequest) {
            HttpEntityEnclosingRequest entityEnclosingRequest = (HttpEntityEnclosingRequest) request;

            StringWriter stringWriter = new StringWriter();
            OutputStream outputStream = new WriterOutputStream(stringWriter);
            try {
                entityEnclosingRequest.getEntity().writeTo(outputStream);
                return stringWriter.toString();
            } catch (IOException e) {
                return e.toString();
            }
        } else {
            return EMPTY;
        }
    }
}
