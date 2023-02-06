package ru.yandex.autotests.metrika.serializers;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.lang3.SerializationException;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;

import java.io.IOException;
import java.util.List;

/**
 * Created by okunev on 21.11.2014.
 * Класс десериализации ответа от сервиса в StatV1DataCsvSchema объект
 */
public class CsvDeserializer {

    public StatV1DataCsvSchema fromResponse(Long code, String message, String content) {
        if (code == 200L) {
            List<CSVRecord> data;
            try {
                data = CSVParser.parse(content, CSVFormat.EXCEL).getRecords();
            } catch (IOException e) {
                throw new SerializationException("Ответ не может быть десериализован в csv", e);
            }

            return new StatV1DataCsvSchema().withResponse(content).withData(data);
        } else {
            return new StatV1DataCsvSchema().withCode(code).withMessage(message);
        }
    }

}
