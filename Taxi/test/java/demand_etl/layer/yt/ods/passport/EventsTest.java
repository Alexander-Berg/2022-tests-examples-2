package demand_etl.layer.yt.ods.passport;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SuppressWarnings("unused")
public class EventsTest {
    @ParameterizedTest
    @MethodSource
    public void testExtractRawPlatform(String rawPlatform, String expected) {
        assertEquals(expected, Events.extractRawPlatform(rawPlatform));
    }

    private static Stream<Arguments> testExtractRawPlatform() {
        return Stream.of(
                Arguments.of(null, null),
                Arguments.of("iPhone", "iphone"),
                Arguments.of("Android 5.1.1 (REL)", "android"),
                Arguments.of("Android 10 (REL)", "android"),
                Arguments.of("Android 7.0 (REL)\t", "android")
        );
    }

    @ParameterizedTest
    @MethodSource
    public void testExtractUuid(String rawUuid, String expected) {
        assertEquals(expected, Events.extractUuid(rawUuid));
    }

    private static Stream<Arguments> testExtractUuid() {
        return Stream.of(
                Arguments.of(null, null),
                Arguments.of("61e6289b4e14c3ba64036014f96afd1e", "61e6289b4e14c3ba64036014f96afd1e"),
                Arguments.of("CE1F093DA39F4DFFA0B187AEAD6ED8C4", "ce1f093da39f4dffa0b187aead6ed8c4"),
                Arguments.of("ce1f093d-a39f-4dff-a0b1-87aead6ed8c4", null),
                Arguments.of("Wowan", null)
        );
    }
}
