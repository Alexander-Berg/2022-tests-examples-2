package ru.yandex.autotests.metrika.core.response;

import com.google.gson.JsonParser;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.autotests.metrika.data.report.v1.enums.FormatEnum;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;
import ru.yandex.autotests.metrika.utils.AllureUtils;

import static ru.yandex.autotests.metrika.core.MetrikaJson.GSON_RESPONSE;

/**
 * Created by konkov on 26.09.2014.
 */
public class MetrikaJsonResponse extends MetrikaBaseResponse {

    public static final String CONTENT_TYPE = FormatEnum.JSON.getMimeType();

    private static final Logger log = LogManager.getLogger(MetrikaJsonResponse.class);

    private static final JsonParser jsonParser = new JsonParser();

    public MetrikaJsonResponse(BackEndResponse backEndResponse) {
        super(backEndResponse);
    }

    public <T> T readResponse(Class<T> clazz) {
        validate();

        return GSON_RESPONSE.fromJson(backEndResponse.getResponseContent().asString(), clazz);
    }

    public void validate() throws MetrikaApiException {
        logHeaders();
        logResponse();

        if (!backEndResponse.getResponseContent().getType().getMimeType().equals(CONTENT_TYPE)) {
            throw new MetrikaApiException(String.format(
                    "Получен неожиданный ответ от сервера. Ожидался JSON, но получено: %s, ошибка: %d %s",
                    backEndResponse.getResponseContent().getType(),
                    backEndResponse.getStatusLine().getStatusCode(),
                    backEndResponse.getStatusLine().getReasonPhrase()));
        }
    }

    private void logResponse() {
        log.info("Response");

        String responseContent = backEndResponse.getResponseContent().asString();

        try {
            log.info(responseContent);

            //try beautify json, otherwise log plain text
            String aContent;
            try {
                aContent = GSON_RESPONSE.toJson(jsonParser.parse(responseContent));
            } catch (Throwable e) {
                aContent = responseContent;
            }
            AllureUtils.addJsonAttachment("Response", aContent);
        } catch (OutOfMemoryError oom) {
            log.warn(
                    String.format("OutOfMemoryError in logResponse, length=%s",
                            responseContent.length()),
                    oom);

            StringBuilder stringBuilder = new StringBuilder()
                    .append("Слишком длинный ответ ручки. Необходимо изменить запрос.").append(System.lineSeparator())
                    .append(String.format("Длина: %s", responseContent.length())).append(System.lineSeparator())
                    .append(ExceptionUtils.getStackTrace(oom));

            AllureUtils.addTextAttachment(String.format("Response (OutOfMemoryError response length=%s)",
                    responseContent.length()),
                    stringBuilder.toString());
        }
    }
}
