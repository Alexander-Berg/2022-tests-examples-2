package ru.yandex.autotests.metrika.utils;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class UtilsTest {

    @Test
    public void changesCaseToLowerWhenUpperCase() {
        assertEquals("abc", Utils.invertCase("ABC"));
    }

    @Test
    public void changesCaseToUpperWhenLowerCase() {
        assertEquals("ABC", Utils.invertCase("abc"));
    }

    @Test
    public void invertsCaseWhenMixedCase() {
        assertEquals("aBc", Utils.invertCase("AbC"));
    }

    @Test
    public void invertCaseMethodIgnoresNonAlphabetSymbols() {
        assertEquals("!@#_", Utils.invertCase("!@#_"));
    }
}
