package ru.yandex.autotests.mordabackend.utils;

import org.joda.time.LocalDateTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25/11/14
 */
public class TimeUtils {

    public static LocalDateTime parseHiddenTime(String hiddenTime) {
        DateTimeFormatter formatter = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss");
        return LocalDateTime.parse(hiddenTime, formatter);
    }

}
