package ru.yandex.autotests.metrika.appmetrica.core;

import com.google.gson.Gson;
import org.apache.http.entity.ContentType;
import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.httpclientlite.core.response.AbstractResponseParser;

import java.util.Collections;
import java.util.List;
import java.util.regex.Pattern;

public class AppMetricaJsonResponseParser extends AbstractResponseParser {

    private final Gson gson;

    public AppMetricaJsonResponseParser(Gson gson) {
        this.gson = gson;
    }

    @Override
    public <T> T actualParse(Response response, Class<T> contentClass) {
        return gson.fromJson(response.getResponseContent().asString(), contentClass);
    }

    @Override
    protected List<ContentType> getAcceptedContentTypes() {
        return Collections.singletonList(ContentType.APPLICATION_JSON);
    }

    @Override
    protected Pattern getStatusCodePattern() {
        return null;
    }
}
