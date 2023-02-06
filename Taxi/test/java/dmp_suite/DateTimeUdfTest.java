package dmp_suite;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class DateTimeUdfTest {
    @ParameterizedTest
    @MethodSource("timestamps")
    void mskToUtc(String date, String expected) {
        assertEquals(expected, DateTimeUdf.mskToUtc(date));
    }

    @ParameterizedTest
    @MethodSource("timestamps")
    void utcToMsk(String expected, String date) {
        assertEquals(expected, DateTimeUdf.utcToMsk(date));
    }

    public static Stream<Arguments> timestamps() {
        return Stream.of(
                Arguments.of("2019-05-21 14:00:02", "2019-05-21 11:00:02"),
                Arguments.of("2019-05-21 00:00:00", "2019-05-20 21:00:00")
        );
    }


    @ParameterizedTest
    @MethodSource
    public void tsToUtcTimestampTest( String expected,Long ts) {
        assertEquals(expected, DateTimeUdf.tsToUtcDateTime(ts));
    }

    private static Stream<Arguments> tsToUtcTimestampTest() {
        long ts1 = Long.parseUnsignedLong("1617379685595");
        long ts2 = Long.parseUnsignedLong("1579522097000");
        long ts3 = Long.parseUnsignedLong("1632406262713");
        return Stream.of(
                Arguments.of("2021-04-02 16:08:05.595000", ts1),
                Arguments.of("2020-01-20 12:08:17.000000", ts2),
                Arguments.of("2021-09-23 14:11:02.713000", ts3)
        );
    }
}
