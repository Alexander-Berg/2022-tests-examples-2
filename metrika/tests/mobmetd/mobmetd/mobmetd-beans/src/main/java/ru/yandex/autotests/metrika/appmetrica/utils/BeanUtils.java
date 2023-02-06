package ru.yandex.autotests.metrika.appmetrica.utils;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Date;


public class BeanUtils {

    private static final DateTimeFormatter ISO_LOCAL_DATE_TIME_WITH_SPACE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static Date parseIsoDtfWithSpace(String text) {
        LocalDateTime dateTime = LocalDateTime.parse(text, ISO_LOCAL_DATE_TIME_WITH_SPACE);
        return Date.from(dateTime.atZone(ZoneId.systemDefault()).toInstant());
    }

    private BeanUtils() {
    }
}
