package ru.yandex.autotests.metrika.core.response;

import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.data.report.v1.enums.FormatEnum;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;
import ru.yandex.autotests.metrika.serializers.XlsxDeserializer;
import ru.yandex.autotests.metrika.utils.AllureUtils;

/**
 * Created by okunev on 21.11.2014.
 */
public class MetrikaXlsxResponse extends MetrikaBaseResponse {

    public static final String CONTENT_TYPE = FormatEnum.XLSX.getMimeType();

    private static final Logger log = LogManager.getLogger(MetrikaXlsxResponse.class);

    private static final XlsxDeserializer xlsx = new XlsxDeserializer();

    public MetrikaXlsxResponse(BackEndResponse backEndResponse) {
        super(backEndResponse);
    }

    public StatV1DataXlsxSchema readResponse() {
        validate();
        return xlsx.fromResponse(
                (long) backEndResponse.getStatusLine().getStatusCode(),
                backEndResponse.getStatusLine().getReasonPhrase(),
                backEndResponse.getResponseContent().asBytes());
    }

    public void validate() throws MetrikaApiException {
        logHeaders();
        logResponse();

        if (!backEndResponse.getResponseContent().getType().getMimeType().equals(CONTENT_TYPE)) {
            throw new MetrikaApiException(String.format(
                    "Получен неожиданный ответ от сервера. Ожидался XLSX, но получено: %s, ошибка: %d %s",
                    backEndResponse.getResponseContent().getType(),
                    backEndResponse.getStatusLine().getStatusCode(),
                    backEndResponse.getStatusLine().getReasonPhrase()));
        }
    }

    private void logResponse() {
        log.info(String.format("XLSX content: %s bytes", backEndResponse.getResponseContent().asBytes().length));
        AllureUtils.addXlsxAttachment("Response", backEndResponse.getResponseContent().asBytes());
    }
}
