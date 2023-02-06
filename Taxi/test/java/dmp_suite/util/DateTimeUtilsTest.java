package dmp_suite.util;


import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.time.*;
import java.time.temporal.TemporalAccessor;
import java.time.temporal.TemporalQuery;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;

class DateTimeUtilsTest {
    @ParameterizedTest
    @MethodSource()
    void testUltimateParser(String raw, TemporalQuery<TemporalAccessor> query, TemporalAccessor expected) {
        TemporalAccessor result = DateTimeUtils.ULTIMATE_FORMATTER.parse(raw, query);
        assertEquals(expected, result);
    }

    private static <DT extends TemporalAccessor> Arguments q(String raw, TemporalQuery<DT> query, DT date) {
        return Arguments.of(raw, query, date);
    }

    public static Stream<Arguments> testUltimateParser() {
        return Stream.of(
                q("2020", Year::from, Year.of(2020)),
                q("2020-02", YearMonth::from, YearMonth.of(2020, 2)),
                q("2020-02-13", LocalDate::from, LocalDate.of(2020, 2, 13)),
                q("2020/02/13", LocalDate::from, LocalDate.of(2020, 2, 13)),
                q("2020-02-13 14:37", LocalDateTime::from, LocalDateTime.of(2020, 2, 13, 14, 37)),
                q("2020.02.13T14:37", LocalDateTime::from, LocalDateTime.of(2020, 2, 13, 14, 37)),
                q("2020-02-13 14:37:16", LocalDateTime::from, LocalDateTime.of(2020, 2, 13, 14, 37, 16)),
                q("2020.02.13 14.37.16", LocalDateTime::from, LocalDateTime.of(2020, 2, 13, 14, 37, 16)),
                q("2020-02-13 14:37:16.345", LocalDateTime::from, LocalDateTime.of(2020, 2, 13, 14, 37, 16, 345*1000000)),
                q("2020-02-13 14:37:16.345678", LocalDateTime::from, LocalDateTime.of(2020, 2, 13, 14, 37, 16, 345678*1000)),
                q("2020-02-13T14:37:16Z", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 0, DateTimeUtils.UTC)),
                q("2020-02-13 14:37:16+0000", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 0, DateTimeUtils.UTC)),
                q("2020-02-13 14:37:16.345678+0000", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 345678*1000, DateTimeUtils.UTC)),
                q("2020-02-13 14:37:16[Europe/London]", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 0, ZoneId.of("Europe/London"))),
                q("2020-02-13 14:37:16+0300", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 0, ZoneOffset.of("+0300"))),
                q("2020-02-13 14:37:16 +0300", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 0, ZoneOffset.of("+0300"))),
                q("2020-02-13 14:37:16[Europe/Moscow]", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 0, DateTimeUtils.MSK)),
                q("2020-02-13 14:37:16 Europe/Moscow", ZonedDateTime::from, ZonedDateTime.of(2020, 2, 13, 14, 37, 16, 0, DateTimeUtils.MSK))
        );
    }

    @ParameterizedTest
    @MethodSource()
    void testConvertDateStringTz(String input, String expected, ZoneId origin, ZoneId target) {
        String result = DateTimeUtils.convertDateTimeStringTz(input, origin, target);
        assertEquals(expected, result);
    }

    public static Stream<Arguments> testConvertDateStringTz() {
        return Stream.of(
                Arguments.of("2019-05-21 14:00:02", "2019-05-21 11:00:02", DateTimeUtils.MSK, DateTimeUtils.UTC),
                Arguments.of("2019-05-21 00:00:00", "2019-05-20 21:00:00", DateTimeUtils.MSK, DateTimeUtils.UTC),
                Arguments.of("2019-05-21 00:00:00", "2019-05-21 00:00:00", DateTimeUtils.MSK, DateTimeUtils.MSK),
                Arguments.of("2019-05-21 00:00:00", "2019-05-21 00:00:00", DateTimeUtils.UTC, DateTimeUtils.UTC),
                Arguments.of("2019-05-20 21:00:00", "2019-05-21 00:00:00", DateTimeUtils.UTC, DateTimeUtils.MSK),
                Arguments.of("2019-05-20 21:00:00", "2019-05-21 00:00:00", DateTimeUtils.UTC, DateTimeUtils.MSK)
        );
    }

}