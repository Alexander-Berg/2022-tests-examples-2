package ru.yandex.autotests.metrika.converters;

import org.apache.commons.csv.CSVRecord;

import java.util.List;
import java.util.function.Function;

import static org.apache.commons.collections4.IteratorUtils.toList;

/**
 * Created by konkov on 16.04.2015.
 */
public class CSVRecordToStringListConverter implements Function<CSVRecord, List<String>> {
    @Override
    public List<String> apply(CSVRecord data) {
        return toList(data.iterator());
    }

    public static CSVRecordToStringListConverter csvToStringList() {
        return new CSVRecordToStringListConverter();
    }
}
