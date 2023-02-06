package ru.yandex.metrika.cdp.common;

import java.util.List;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import static org.junit.Assert.assertEquals;

public class CsvParsingUtilTest {

    @Rule
    public final ExpectedException expectedException = ExpectedException.none();

    @Test
    public void doNotSplitStringTest() {
        assertExpectedStringSplit("12321", List.of("12321"));
    }

    @Test
    public void simpleSplitStringTest() {
        assertExpectedStringSplit("123,21", List.of("123", "21"));
    }

    @Test
    public void simpleEscapedStringTest() {
        assertExpectedStringSplit("123\\,21", List.of("123,21"));
    }

    @Test
    public void trimWithSplitTest() {
        assertExpectedStringSplit("  12   ,  \t 3 ", List.of("12", "3"));
    }

    @Test
    public void complexEscapedStringTest1() {
        assertExpectedStringSplit("123\\\\,21,00", List.of("123\\", "21", "00"));
    }

    @Test
    public void complexEscapedStringTest2() {
        assertExpectedStringSplit("123\\\\\\,21,00", List.of("123\\,21", "00"));
    }

    @Test
    public void complexEscapedStringTest3() {
        assertExpectedStringSplit("123\\\\,21,00\\,", List.of("123\\", "21", "00,"));
    }

    @Test
    public void failureOnBackslashAtTheEndStringTest() {
        expectedException.expect(EscapingException.class);
        expectedException.expectMessage("\\ at the end of string");
        CsvParsingUtil.splitWithTrimStringByCommaEscaped("123\\");
    }

    @Test
    public void failureOnWrongEscapingSequenceStringTest() {
        expectedException.expect(EscapingException.class);
        expectedException.expectMessage("wrong escaping sequence \"\\a\"");
        CsvParsingUtil.splitWithTrimStringByCommaEscaped("123\\a");
    }

    @Test
    public void doNotSplitNumberTest() {
        assertExpectedLongSplit("12321", List.of(12321L));
    }

    @Test
    public void simpleSplitNumberTest() {
        assertExpectedLongSplit("123,12", List.of(123L, 12L));
    }

    @Test
    public void splitWithTrimNumberTest() {
        assertExpectedLongSplit(" 123   , \t 11", List.of(123L, 11L));
    }

    @Test
    public void failureOnInvalidNumberTest() {
        expectedException.expect(NumberFormatException.class);
        CsvParsingUtil.splitWithTrimStringByCommaToUnsignedLongs("123, qqq");
    }

    private void assertExpectedStringSplit(String s, List<String> expected) {
        var strings = CsvParsingUtil.splitWithTrimStringByCommaEscaped(s);
        assertEquals(expected, strings);
    }

    private void assertExpectedLongSplit(String s, List<Long> expected) {
        var strings = CsvParsingUtil.splitWithTrimStringByCommaToUnsignedLongs(s);
        assertEquals(expected, strings);
    }
}
