package ru.yandex.autotests.metrika.appmetrica.core;

import com.google.common.base.Throwables;
import com.opencsv.CSVParser;
import com.opencsv.CSVParserBuilder;
import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import org.apache.http.Consts;
import org.apache.http.entity.ContentType;
import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.httpclientlite.core.response.AbstractResponseParser;
import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;

import java.io.IOException;
import java.io.StringReader;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Парсер ответа на запрос csv файла
 *
 * @author dancingelf
 */
public class AppMetricaCsvRawResponseParser extends AbstractResponseParser {

    @Override
    @SuppressWarnings("unchecked")
    protected <T> T actualParse(Response response, Class<T> contentClass) {
        final String data = response.getResponseContent().asString();
        final CSVParser parser = new CSVParserBuilder().withStrictQuotes(true).build();
        try (CSVReader reader = new CSVReaderBuilder(new StringReader(data)).withCSVParser(parser).build()) {
            String[] headers = reader.readNext();
            if (headers == null) {
                throw new AppMetricaException("Не удалось получить заголовок csv файла");
            }
            List<List<String>> content = reader.readAll().stream().map(Arrays::asList).collect(Collectors.toList());
            return (T) new AppMetricaCsvRawResponse(Arrays.asList(headers), content);
        } catch (IOException ex) {
            throw Throwables.propagate(ex);
        }
    }

    @Override
    protected List<ContentType> getAcceptedContentTypes() {
        return Collections.singletonList(ContentType.create("application/csv", Consts.UTF_8));
    }

    @Override
    protected List<Class<?>> getSupportedReturnTypes() {
        return Collections.singletonList(AppMetricaCsvRawResponse.class);
    }
}
