package ru.yandex.autotests.metrika.core;

import ch.lambdaj.function.convert.DefaultStringConverter;
import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.ResponseHandler;
import org.apache.http.entity.BufferedHttpEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.util.EntityUtils;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.autotests.httpclient.lite.core.ResponseContent;
import ru.yandex.autotests.metrika.core.response.MetrikaCsvResponse;
import ru.yandex.autotests.metrika.core.response.MetrikaJavaScriptResponse;
import ru.yandex.autotests.metrika.core.response.MetrikaJsonResponse;
import ru.yandex.autotests.metrika.core.response.MetrikaXlsxResponse;
import ru.yandex.autotests.metrika.data.report.v1.enums.FormatEnum;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static org.hamcrest.Matchers.hasKey;
import static org.hamcrest.Matchers.startsWith;

/**
 * Created by konkov on 26.09.2014.
 */
public class MetrikaResponseHandler implements ResponseHandler<BackEndResponse> {

    private static final Logger log = LogManager.getLogger(MetrikaResponseHandler.class);

    private static final Gson gson = new GsonBuilder()
            .setFieldNamingStrategy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
            .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
            .create();

    @Override
    public BackEndResponse handleResponse(HttpResponse response) throws IOException {
        StatusLine statusLine = response.getStatusLine();
        HttpEntity entity = new BufferedHttpEntity(response.getEntity());

        tryHandleTimedOut(statusLine, entity);

        log.info(String.format("Content-type: %s", entity.getContentType().getValue()));

        return new BackEndResponse(statusLine, entity, response.getAllHeaders());

    }

    private void tryHandleTimedOut(StatusLine statusLine, HttpEntity entity) {
        if (statusLine.getStatusCode() == 503) {
                String stringResponse = getResponseContent(entity);
                if (hasReadTimedOut(stringResponse)) {
                    //?????????????????????? ?????????????????????? ???????????????????? ?? ?????????????????????????? ??????????
                    log.trace(stringResponse);
                    throw new MetrikaApiException("Read timed out; Relaunch recommended.");
                }
        }
    }

    private String getResponseContent(HttpEntity entity) {
        String stringResponse = null;

        try {
            ResponseContent responseContent =
                    new ResponseContent(EntityUtils.toByteArray(entity), ContentType.getOrDefault(entity));

            stringResponse = responseContent.asString();
        } catch (Throwable e) {
            log.warn("Error in retrieving response content", e);
            log.trace(ExceptionUtils.getStackTrace(e));
        }

        return stringResponse;
    }

    private boolean hasReadTimedOut(String responseContent) {
        boolean result = false;

        try {
            Map response = gson.fromJson(responseContent, Map.class);

            String readTimedOut = with((List<Map>) PropertyUtils.getProperty(response, "_profile.queries"))
                    .retain(hasKey("error_message"))
                    .extract(on(Map.class).get("error_message"))
                    .convert(new DefaultStringConverter())
                    .first(startsWith("Read timed out;"));

            result = !StringUtils.isEmpty(readTimedOut);

        } catch (Throwable e) {
            log.warn("Error in parsing response content", e);
            log.trace(responseContent);
            log.trace(ExceptionUtils.getStackTrace(e));
        }

        return result;
    }
}
