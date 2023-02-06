package ru.yandex.autotests.morda.utils.cookie.parsers.my;

import org.junit.Test;

/**
 * User: leonsabr
 * Date: 24.06.12
 */
public class ParseInvalidCookieTest {
    @Test(expected = NullPointerException.class)
    public void checkNullInput() {
        String my = null;
        MyCookieParser.parse(my);
    }

    @Test(expected = IllegalArgumentException.class)
    public void checkIncorrectFirstByteInput() {
        MyCookieParser.parse("some stuff here");
    }

    @Test(expected = ArrayIndexOutOfBoundsException.class)
    public void checkInvalidCookieTest() {
        MyCookieParser.parse("YygBAkI2AQEA");
    }
}
