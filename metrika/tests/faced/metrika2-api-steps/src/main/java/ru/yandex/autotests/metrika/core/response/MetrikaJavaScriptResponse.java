package ru.yandex.autotests.metrika.core.response;

import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.autotests.metrika.data.report.v1.enums.FormatEnum;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;
import ru.yandex.autotests.metrika.utils.AllureUtils;

/**
 * Created by konkov on 20.02.2015.
 */
public class MetrikaJavaScriptResponse extends MetrikaBaseResponse {

    public static final String CONTENT_TYPE = FormatEnum.JAVASCRIPT.getMimeType();

    private static final Logger log = LogManager.getLogger(MetrikaJavaScriptResponse.class);

    public MetrikaJavaScriptResponse(BackEndResponse backEndResponse) {
        super(backEndResponse);
    }

    public String readResponse() {
        validate();

        return backEndResponse.getResponseContent().asString();
    }

    private void validate() throws MetrikaApiException {
        logHeaders();
        logResponse();

        if (!backEndResponse.getResponseContent().getType().getMimeType().equals(CONTENT_TYPE)) {
            throw new MetrikaApiException(String.format(
                    "Получен неожиданный ответ от сервера. Ожидался JavaScript, но получено: %s, ошибка: %d %s",
                    backEndResponse.getResponseContent().getType(),
                    backEndResponse.getStatusLine().getStatusCode(),
                    backEndResponse.getStatusLine().getReasonPhrase()));
        }
    }

    private void logResponse() {
        log.info("Response");
        log.info(backEndResponse.getResponseContent().asString());

        AllureUtils.addTextAttachment("Response", backEndResponse.getResponseContent().asString());
    }
}
