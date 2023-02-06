package ru.yandex.autotests.metrika.serializers;

import org.apache.commons.lang3.SerializationException;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;

import java.io.ByteArrayInputStream;
import java.io.IOException;

/**
 * Created by okunev on 21.11.2014.
 * Класс десериализации ответа от сервиса в StatV1DataXlsxSchema объект
 */
public class XlsxDeserializer {

    public StatV1DataXlsxSchema fromResponse(Long code, String message, byte[] content) {
        if (code == 200L) {
            XSSFSheet data;
            try {
                data = new XSSFWorkbook(new ByteArrayInputStream(content)).getSheetAt(0);
            } catch (IOException e) {
                throw new SerializationException("Ответ не может быть десериализован в xlsx", e);
            }

            return new StatV1DataXlsxSchema().withResponse(content).withData(data);
        } else {
            return new StatV1DataXlsxSchema().withCode(code).withMessage(message);
        }
    }

}
