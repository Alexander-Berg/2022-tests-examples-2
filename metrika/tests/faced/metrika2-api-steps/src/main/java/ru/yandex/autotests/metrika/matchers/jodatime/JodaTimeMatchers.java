package ru.yandex.autotests.metrika.matchers.jodatime;

import org.hamcrest.Matcher;
import org.joda.time.*;

/**
 * @author zgmnkv
 */
public class JodaTimeMatchers {

    public static Matcher<DateTime> dateTimeWithField(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        return new DateTimeFieldMatcher(fieldType, fieldMatcher);
    }

    public static Matcher<LocalDateTime> localDateTimeWithField(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        return new LocalDateTimeFieldMatcher(fieldType, fieldMatcher);
    }

    public static Matcher<LocalDate> localDateWithField(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        return new LocalDateFieldMatcher(fieldType, fieldMatcher);
    }

    public static Matcher<LocalTime> localTimeWithField(DateTimeFieldType fieldType, Matcher<Integer> fieldMatcher) {
        return new LocalTimeFieldMatcher(fieldType, fieldMatcher);
    }

    public static Matcher<DateTime> dateTimeWithTimeZoneOffset(Matcher<Integer> offsetMatcher) {
        return new TimeZoneOffsetMatcher(offsetMatcher);
    }
}
