package ru.yandex.autotests.metrika.appmetrica.core;

import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.httpclientlite.core.response.AbstractResponseParser;
import ru.yandex.autotests.metrika.appmetrica.body.CustomEntityBody;

import static org.apache.http.HttpHeaders.CONTENT_TYPE;

public class CustomEntityResponseParser extends AbstractResponseParser {
    @Override
    @SuppressWarnings("unchecked")
    protected <T> T actualParse(Response response, Class<T> aClass) {
        String contentType = response.getHeader(CONTENT_TYPE).getValue();
        byte[] content = response.getResponseContent().asBytes();
        return (T) new CustomEntityBody(contentType, content);
    }
}
