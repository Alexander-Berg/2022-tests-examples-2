package ru.yandex.metrika.util.url;


import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class IDNUtilTest {


    @Test
    public void testAsciiToAscii() {
        final String site = "metrika.yandex.ru";
        final String asciiSite = IDNUtils.toASCII(site);

        assertEquals(site, asciiSite);
    }

    @Test
    public void testUnicodeToAscii() {
        final String site = "призедент.рф";
        final String punycode = "xn--d1abbfe8aiiy.xn--p1ai";
        final String asciiSite = IDNUtils.toASCII(site);

        assertTrue(IDNUtils.isASCII(asciiSite));
        assertEquals(punycode, asciiSite);
    }

    @Test
    public void testAsciiToUnicode() {
        final String site = "призедент.рф";
        final String punycode = "xn--d1abbfe8aiiy.xn--p1ai";
        final String unicodeSite = IDNUtils.toUnicode(punycode);

        assertEquals(site, unicodeSite);
    }

    @Test
    public void testValidation() {
        assertTrue(IDNUtils.isValid("google.com"));
        assertTrue(IDNUtils.isValid("http://google.com"));
        assertTrue(IDNUtils.isValid("google.com."));
        assertTrue(IDNUtils.isValid("google.ru"));
        assertTrue(IDNUtils.isValid("ya.ru"));
        assertTrue(IDNUtils.isValid("ya.ru"));
        assertTrue(IDNUtils.isValid("test_test.ru"));
        assertTrue(IDNUtils.isValid("https://test_test.ru"));
        assertTrue(IDNUtils.isValid("призедент.рф"));
        assertTrue(IDNUtils.isValid("xn--d1abbfe8aiiy.xn--p1ai"));
        assertTrue(IDNUtils.isValid("призедент_призедент.рф"));
        assertTrue(IDNUtils.isValid("http://призедент_призедент.рф"));
        assertTrue(IDNUtils.isValid("xn--_-gtbbbbbbjeef2dgphii7aj.xn--p1ai"));

        assertFalse(IDNUtils.isValid("!@#$.ru"));
        assertFalse(IDNUtils.isValid("https://!@#$.ru"));
        assertFalse(IDNUtils.isValid("!@#$.рф"));
        assertFalse(IDNUtils.isValid("test,test.com"));
        assertFalse(IDNUtils.isValid("http://test,test.com"));
        assertFalse(IDNUtils.isValid("запятая,запятая.рф"));
    }


}
