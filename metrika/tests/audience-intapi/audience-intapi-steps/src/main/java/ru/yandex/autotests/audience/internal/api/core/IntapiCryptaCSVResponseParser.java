package ru.yandex.autotests.audience.internal.api.core;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.http.entity.ContentType;
import ru.yandex.autotests.audience.internal.api.schema.custom.SegmentDataSchema;
import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.httpclientlite.core.response.AbstractResponseParser;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Created by apuzikov on 14.07.17.
 */
public class IntapiCryptaCSVResponseParser extends AbstractResponseParser {

    @Override
    protected <T> T actualParse(Response response, Class<T> contentClass) {
        try {
            return (T) CSVParser.parse(response.getResponseContent().asString(), CSVFormat.EXCEL).getRecords();
        } catch (IOException e) {
            throw new CryptaDeserializerException("Can't deserialize result into csv. Response -" + response, e);
        }
    }

    @Override
    protected List<Class<?>> getSupportedReturnTypes() {
        return Collections.singletonList(SegmentDataSchema.class);
    }

    @Override
    protected List<ContentType> getAcceptedContentTypes() {
        return Arrays.asList(ContentType.TEXT_PLAIN);
    }
}
