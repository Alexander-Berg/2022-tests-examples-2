package ru.yandex.metrika.util;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * Created by vesel4ak-u on 24.03.16.
 */
public class WildcardTest {

    @Test
    public void testDoubleAll() {
        assertEquals("123\\\\abc''", Wildcard.doubleAll("123\\abc'", '\\', '\''));
    }
}
