package ru.yandex.metrika.spring.params;

import org.junit.Test;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class HexadecimalTest {
    @Test
    public void testEmpty() {
        Hexadecimal.Validator validator = new Hexadecimal.Validator();
        assertTrue(validator.isValid("", null));
    }

    @Test
    public void testNull() {
        Hexadecimal.Validator validator = new Hexadecimal.Validator();
        assertTrue(validator.isValid(null, null));
    }

    @Test
    public void testAllDigits() {
        Hexadecimal.Validator validator = new Hexadecimal.Validator();
        assertTrue(validator.isValid("0123456789abcdef", null));
    }

    @Test
    public void testUpperCase() {
        Hexadecimal.Validator validator = new Hexadecimal.Validator();
        assertTrue(validator.isValid("0123456789ABCDEF", null));
    }

    @Test
    public void testIllegalDigitFails() {
        Hexadecimal.Validator validator = new Hexadecimal.Validator();
        assertFalse(validator.isValid("g", null));
    }

    @Test
    public void testSpacesFails() {
        Hexadecimal.Validator validator = new Hexadecimal.Validator();
        assertFalse(validator.isValid(" 0123456789abcdef", null));
    }
}
