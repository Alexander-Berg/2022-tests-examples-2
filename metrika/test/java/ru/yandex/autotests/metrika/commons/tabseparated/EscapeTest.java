package ru.yandex.autotests.metrika.commons.tabseparated;

import com.google.common.collect.ImmutableMap;
import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;

public class EscapeTest {

    @Test
    public void testEscape() {
        Map<Byte, Byte> mapping = ImmutableMap.<Byte, Byte>builder()
                .put((byte) 0x0, (byte) 0x30)
                .put(Escape.BACK_SLASH, Escape.BACK_SLASH)
                .build();

        assertThat(Escape.escape(mapping, "\\\0".getBytes(StandardCharsets.UTF_8)),
                equalTo("\\\\\\0".getBytes(StandardCharsets.UTF_8)));
    }

    @Test
    public void testUnEscape() {
        Map<Byte, Byte> mapping = ImmutableMap.<Byte, Byte>builder()
                .put((byte) 0x30, (byte) 0x0)
                .put(Escape.BACK_SLASH, Escape.BACK_SLASH)
                .build();

        assertThat(Escape.unescape(mapping, "\\\\\\0".getBytes(StandardCharsets.UTF_8)),
                equalTo("\\\0".getBytes(StandardCharsets.UTF_8)));
    }

    @Test
    public void testIsEscaped() {
        byte[] data = "\\t".getBytes(StandardCharsets.UTF_8);

        assertThat(Escape.isEscaped(data, 1), equalTo(true));
    }

    @Test
    public void testIsNotEscaped() {
        byte[] data = "ab".getBytes(StandardCharsets.UTF_8);

        assertThat(Escape.isEscaped(data, 1), equalTo(false));
    }
}
