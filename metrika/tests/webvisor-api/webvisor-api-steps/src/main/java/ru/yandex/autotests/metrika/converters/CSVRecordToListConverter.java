package ru.yandex.autotests.metrika.converters;

import org.apache.commons.csv.CSVRecord;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;


public class CSVRecordToListConverter implements Function<CSVRecord, List<Object>> {

    @Override
    public List<Object> apply(CSVRecord data) {
        List<Object> result = new ArrayList<>();
        for (String value : data) {
            result.add(isNumeric(value) ? Double.parseDouble(value) : value);
        }
        return result;
    }

    public static CSVRecordToListConverter csvToList() {
        return new CSVRecordToListConverter();
    }

    private boolean isNumeric(String str) {
        if (str == null
            || str.isEmpty()
            || str.indexOf('.') != str.lastIndexOf('.')
            || str.indexOf('-') != str.lastIndexOf('-')
            || (str.indexOf('-') != -1 && str.indexOf('-') != 0)) {
            return false;
        } else {
            int sz = str.length();

            for (int i = 0; i < sz; ++i) {
                if (!Character.isDigit(str.charAt(i)) && !(str.charAt(i) == '.') && !(str.charAt(i) == '-')) {
                    return false;
                }
            }

            return true;
        }
    }
}
