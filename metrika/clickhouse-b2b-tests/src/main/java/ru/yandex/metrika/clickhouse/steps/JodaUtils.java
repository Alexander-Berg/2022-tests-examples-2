package ru.yandex.metrika.clickhouse.steps;

import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.DateTimeFormatterBuilder;
import org.joda.time.format.PeriodFormatter;
import org.joda.time.format.PeriodFormatterBuilder;

public class JodaUtils {
    private JodaUtils() {}

    public static final DateTimeFormatter DTF = new DateTimeFormatterBuilder()
            .appendYear(4, 4)
            .appendLiteral(".")
            .appendMonthOfYear(2)
            .appendLiteral(".")
            .appendDayOfMonth(2)
            .appendLiteral(" ")
            .appendHourOfDay(2)
            .appendLiteral(":")
            .appendMinuteOfHour(2)
            .appendLiteral(":")
            .appendSecondOfMinute(2)
            .toFormatter();

    public static final PeriodFormatter PF = new PeriodFormatterBuilder()
            .printZeroAlways()
            .appendHours()
            .appendLiteral(":")
            .appendMinutes()
            .appendLiteral(":")
            .appendSecondsWithOptionalMillis()
            .toFormatter();
}
