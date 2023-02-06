package ru.yandex.metrika.spring.params;

import org.junit.Test;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class MsqlUtf8CharsetTest {

    @Test
    public void testEmpty() {
        MysqlUtf8Charset.Validator validator = new MysqlUtf8Charset.Validator();
        assertTrue(validator.isValid("", null));
    }

    @Test
    public void testNull() {
        MysqlUtf8Charset.Validator validator = new MysqlUtf8Charset.Validator();
        assertTrue(validator.isValid(null, null));
    }

    @Test
    public void testSimpleString() {
        MysqlUtf8Charset.Validator validator = new MysqlUtf8Charset.Validator();
        assertTrue(validator.isValid("Простая строка без 4-х байтовых символов ௸", null));
    }

    @Test
    public void testSingle4BytesSymbol() {
        MysqlUtf8Charset.Validator validator = new MysqlUtf8Charset.Validator();
        assertFalse(validator.isValid("\uD83D\uDC7D", null));
    }

    @Test
    public void testStringWith4BytesSymbol() {
        MysqlUtf8Charset.Validator validator = new MysqlUtf8Charset.Validator();
        assertFalse(validator.isValid("Строка с 4-х байтовым символом: \uD83D\uDC7D", null));
    }
}
