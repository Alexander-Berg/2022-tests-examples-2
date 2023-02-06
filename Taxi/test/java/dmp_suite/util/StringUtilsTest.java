package dmp_suite.util;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class StringUtilsTest {

    @ParameterizedTest
    @MethodSource()
    void testNormalize(String raw, String normalized) {
        assertEquals(normalized, StringUtils.normalize(raw).orElse(null));
    }

    public static Stream<Arguments> testNormalize() {
        return Stream.of(
                Arguments.of(null, null),
                Arguments.of("", ""),
                Arguments.of("авс", "ABC"),
                Arguments.of("abc", "ABC"),
                Arguments.of("АБВ где 1", "AБBГДE1"),
                Arguments.of("АБВ XYZ 2!?", "AБBXYZ2"),
                Arguments.of("ХАЙУ-Хай!взЗ", "XAЙYXAЙB33"),
                Arguments.of("УКЕНТРАЯК1234", "YKEHTPAЯK1234")
        );
    }
}
