package ru.yandex.metrika.util;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.Assert.assertEquals;

/**
 * @author jkee
 */

public class StringUtilTest {

    @Test
    public void testMd5() {
        assertEquals("fe1f78394dda66ace79ae0dc294a6dd3", StringUtil.stringMd5("79295641501"));
    }

    @Test
    public void testSplit4() {
        String s = "\"\"";
        String[] split = StringUtil.splitWithoutEscaped(s, '\"', true);
        assertEquals(3, split.length);
        assertEquals("", split[0]);
        assertEquals("", split[1]);
        assertEquals("", split[2]);
    }

    @Test
    public void testSplit() {
        String s = ";olokokok;fdsfdsfds;fdsfada\\;das\\zdada;";
        String[] split = StringUtil.splitWithoutEscaped(s, ';');
        assertEquals("olokokok", split[0]);
        assertEquals("fdsfdsfds", split[1]);
        assertEquals("fdsfada\\;das\\zdada", split[2]);
        assertEquals("\\;zxvc", StringUtil.splitWithoutEscaped("\\;zxvc", ';')[0]);
    }


    @Test
    public void testSplit2() {
        String s = "lokokok;zdsfdsfds;ddsfad\\;da\\;das\\z;dada;";
        String[] split = StringUtil.splitWithoutEscaped(s, ";d");
        assertEquals("lokokok;zdsfdsfds", split[0]);
        assertEquals("dsfad\\;da\\;das\\z", split[1]);
        assertEquals("ada;", split[2]);
    }

    @Test
    public void testSplitIgnoreQuoted() {
        String s = "lok\"o\"kok;\"zdsfdsfds\";fa\\\"zvx;zzz\"qq;zz\"czx\"\"";
        String[] split = StringUtil.splitIgnoreQuoted(s, ';', '\"');
        assertEquals("lok\"o\"kok", split[0]);
        assertEquals("\"zdsfdsfds\"", split[1]);
        assertEquals("fa\\\"zvx", split[2]);
        assertEquals("zzz\"qq;zz\"czx\"\"", split[3]);
    }

    @Test
    public void testIndexOf() {
        assertEquals(3, StringUtil.indexOfIgnoreQuoted("\"\"1234", "2", '\"'));
        assertEquals(2, StringUtil.indexOfIgnoreQuoted("\"\"1234", "1", '\"'));
        assertEquals(5, StringUtil.indexOfIgnoreQuoted("\"\"1234", "4", '\"'));

        assertEquals(1, StringUtil.indexOfIgnoreQuoted("lok\"o\"kok", "o", '\"'));
        assertEquals(7, StringUtil.indexOfIgnoreQuoted("lzk\"o\"kok", "o", '\"'));

        assertEquals(1, StringUtil.indexOfIgnoreQuoted("lok\"o\"kok", "o", '\"', 0));
        assertEquals(1, StringUtil.indexOfIgnoreQuoted("lok\"o\"kok", "o", '\"', 1));
        assertEquals(7, StringUtil.indexOfIgnoreQuoted("lok\"o\"kok", "o", '\"', 2));

        assertEquals("lzk\"o\"kok\"zoz\"fffso".length() - 1,
                StringUtil.indexOfIgnoreQuoted("lzk\"o\"kok\"zoz\"fffsoofsdf", "o", '\"', "lzk\"o\"ko".length()));
    }

    @Test
    public void testReplaceIgnoreQuoted() {
        assertEquals("l__k\"o\"k__k", StringUtil.replaceIgnoreQuoted("lok\"o\"kok", "o", "__", '\"'));
    }

    @Test
    public void testRetainUnquoted() {
        assertEquals("lokkok", StringUtil.retainUnquoted("lok\"o\"kok", '\"'));
        assertEquals("lok", StringUtil.retainUnquoted("lok\"o\"", '\"'));
        assertEquals("kok", StringUtil.retainUnquoted("\"o\"kok", '\"'));

    }

    @Test
    public void testSplitConcatenated1() {
        List<String> res = StringUtil.splitConcatenatedWithSeparator("123\\.abc", '.');
        assertEquals(1, res.size());
        assertEquals("123.abc", res.get(0));
    }
    @Test
    public void testSplitConcatenated2() {
        List<String> res = StringUtil.splitConcatenatedWithSeparator("123\\\\.abc", '.');
        assertEquals(2, res.size());
        assertEquals("123\\", res.get(0));
        assertEquals("abc", res.get(1));
    }
    @Test
    public void testSplitConcatenated3() {
        List<String> res = StringUtil.splitConcatenatedWithSeparator("123\\\\\\..abc", '.');
        assertEquals(2, res.size());
        assertEquals("123\\.", res.get(0));
        assertEquals("abc", res.get(1));
    }
    @Test(expected = IllegalArgumentException.class)
    public void testSplitConcatenated4() {
        StringUtil.splitConcatenatedWithSeparator("123\\\\\\abc", '.');
    }
    @Test(expected = IllegalArgumentException.class)
    public void testSplitConcatenated5() {
        StringUtil.splitConcatenatedWithSeparator("\\", '.');
    }

    @Test
    public void testconcatenateWithSeparator() {
        String concatenated = StringUtil.concatenateWithSeparator(Arrays.asList("a.b\\", "A\\.B"), '.');
        assertEquals("a\\.b\\\\.A\\\\\\.B", concatenated);
        List<String> parts = StringUtil.splitConcatenatedWithSeparator(concatenated, '.');
        assertEquals(2, parts.size());
        assertEquals("a.b\\", parts.get(0));
        assertEquals("A\\.B", parts.get(1));
    }

    @Test
    public void testStringMd5() {
        String message = "sergey.serebryanik@yandex.ru";
        assertEquals("d3483f0a6a176454c993c144044deb82", StringUtil.stringMd5(message));
    }

    @Test
    public void testMacMd5() {
        String message = "AE123456D0A1";
        assertEquals("c5b125fd0fdb096c0e29aa896cb044f5", StringUtil.stringMd5(message));
        assertEquals("c5c32c30c07abbb7580a0925d995fee4", StringUtil.stringMd5(StringUtil.hexStringToBytes(message)));
    }

    @Test
    public void testMacMd5Bytes() {
        byte[] message = new byte[] {(byte)0xAE,0x12,0x34,0x56,(byte)0xD0,(byte)0xA1};
        assertEquals("c5c32c30c07abbb7580a0925d995fee4", StringUtil.stringMd5(message));
    }

    @Test
    public void testClickhousify1() {
        assertEquals("nothing", StringUtil.clickHousify("nothing"));
    }

    @Test
    public void testNumberToStringFixedLength1() {
        assertEquals("00123", StringUtil.numberToStringFixedLength(123, 5));
    }

    @Test
    public void testNumberToStringFixedLength2() {
        assertEquals("23456", StringUtil.numberToStringFixedLength(123456, 5));
    }

    @Test
    public void testNumberToStringFixedLength3() {
        assertEquals("12345", StringUtil.numberToStringFixedLength(12345, 5));
    }

    @Test
    public void testBytesToHexString() {
        String s = new String(StringUtil.hexStringToBytes(StringUtil.bytesToHexString("abc".getBytes(StandardCharsets.UTF_8))),StandardCharsets.UTF_8) ;
        assertEquals("abc", s);
    }

    @Test
    public void testEscapeJson() {
        assertEquals(
                "test тест \\\\ \\\" \\b \\f \\n \\r \\t \\u0000 \\u0001 \\u001F   ~ \\u007F",
                StringUtil.escapeJson("test тест \\ \" \b \f \n \r \t \u0000 \u0001 \u001F \u0020 \u007E \u007F")
        );
    }

    @Test
    public void escapeForSingleQuotes() {
        assertThat(StringUtil.escapeForSingleQuotes("\"'\\")).isEqualTo("\"\\'\\\\");
    }

    @Test
    public void escapeBackticks() {
        assertThat(StringUtil.escapeBackticks("abc-d")).isEqualTo("`abc-d`");
    }

    @Test
    public void escapeBackticks2() {
        assertThat(StringUtil.escapeBackticks("abc`-d")).isEqualTo("`abc\\`-d`");
    }

    @Test
    public void escapeBackticks3() {
        assertThat(StringUtil.escapeBackticks("a\nbc\\`-\rd")).isEqualTo("`a\\nbc\\\\\\`-\\rd`");
    }
}
