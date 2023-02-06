package ru.yandex.metrika.common.test.medium;

import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.DateTimeFormatterBuilder;
import org.joda.time.format.DateTimeParser;

public class MultiFormatter {

    public final static DateTimeFormatter dateFormatter = DateTimeFormat.forPattern("yyyy-MM-dd");
    public final static DateTimeFormatter dateTimeFormatter = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss");

    private final static DateTimeParser[] parsers = {dateFormatter.getParser(), dateTimeFormatter.getParser()};

    public final static DateTimeFormatter multiFormatter = new DateTimeFormatterBuilder()
            .append(null, parsers).toFormatter();

}
