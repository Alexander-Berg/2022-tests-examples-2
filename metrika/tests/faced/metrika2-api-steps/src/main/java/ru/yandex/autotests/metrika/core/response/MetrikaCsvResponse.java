package ru.yandex.autotests.metrika.core.response;

import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.data.report.v1.enums.FormatEnum;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;
import ru.yandex.autotests.metrika.serializers.CsvDeserializer;
import ru.yandex.autotests.metrika.utils.AllureUtils;

/**
 * Created by okunev on 21.11.2014.
 */
public class MetrikaCsvResponse extends MetrikaBaseResponse {

    public static final String CONTENT_TYPE = FormatEnum.CSV.getMimeType();

    private static final Logger log = LogManager.getLogger(MetrikaCsvResponse.class);

    private static final CsvDeserializer csv = new CsvDeserializer();

    public MetrikaCsvResponse(BackEndResponse backEndResponse) {
        super(backEndResponse);
    }

    public StatV1DataCsvSchema readResponse() {
        validate();

        return csv.fromResponse(
                (long) backEndResponse.getStatusLine().getStatusCode(),
                backEndResponse.getStatusLine().getReasonPhrase(),
                backEndResponse.getResponseContent().asString());
    }

    private void validate() throws MetrikaApiException {
        logHeaders();
        logResponse();

        if (!backEndResponse.getResponseContent().getType().getMimeType().equals(CONTENT_TYPE)) {
            throw new MetrikaApiException(String.format(
                    "Получен неожиданный ответ от сервера. Ожидалось CSV, но получено: %s, ошибка: %d %s",
                    backEndResponse.getResponseContent().getType(),
                    backEndResponse.getStatusLine().getStatusCode(),
                    backEndResponse.getStatusLine().getReasonPhrase()));
        }
    }

    private void logResponse() {
        log.info("Response");
        log.info(backEndResponse.getResponseContent().asString());
        AllureUtils.addCsvAttachment("Response", backEndResponse.getResponseContent().asString().getBytes());
    }
}
