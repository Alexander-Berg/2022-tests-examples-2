package ru.yandex.metrika.util;

import java.io.UnsupportedEncodingException;

import org.junit.Assert;
import org.junit.Test;

/**
 * @author styopochkin
 * @since 08.09.11
 */
public class MurmurHashTest {
    @Test
    public void testCharHash() throws UnsupportedEncodingException {
        testCharsFromString("ы");
        testCharsFromString("яц");
        testCharsFromString("фуш");
        testCharsFromString("фыця");
        testCharsFromString("фыцяш");
        testCharsFromString("фыцяшs");
        testCharsFromString("фыцяшsw");
        testCharsFromString("fghkerty");
        testCharsFromString("fghkertyu");
    }

    private static void testCharsFromString(String data) {
        byte[] dataBytes = stringToBytes(data);
        Assert.assertEquals(
            MurmurHash.longHash(dataBytes, 0),
            MurmurHash.longHash(data.toCharArray(), 0)
        );
    }

    @Test
    public void testStringHash() throws UnsupportedEncodingException {
        testStringFromString("ы");
        testStringFromString("яц");
        testStringFromString("фуш");
        testStringFromString("фыця");
        testStringFromString("фыцяш");
        testStringFromString("фыцяшs");
        testStringFromString("фыцяшsw");
        testStringFromString("fghkerty");
        testStringFromString("fghkertyu");
    }

    private static void testStringFromString(String data) {
        byte[] dataBytes = stringToBytes(data);
        Assert.assertEquals(
            MurmurHash.longHash(dataBytes, 0),
            MurmurHash.longHash(data, 0)
        );
    }

    static byte[] stringToBytes(String str) {
        byte[] res = new byte[str.length() * 2];
        int bi = 0;
        for (int i = 0; i < str.length(); i++) {
            char ch = str.charAt(i);
            res[bi++] = (byte)((int) ch & 0xFF);
            res[bi++] = (byte)((int) ch >>> 8 & 0xFF);
        }
        return res;
    }

    static String bytesToString(byte[] bytes) {
        StringBuilder sb = new StringBuilder(bytes.length / 2);
        int i = 0;
        while (i < bytes.length) {
            int ich = bytes[i] << 8;
            i++;
            ich |= bytes[i];
            i++;
            sb.append((char)ich);
        }
        return sb.toString();
    }
}
