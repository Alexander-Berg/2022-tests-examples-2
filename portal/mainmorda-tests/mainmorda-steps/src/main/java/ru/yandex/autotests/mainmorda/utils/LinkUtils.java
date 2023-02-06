package ru.yandex.autotests.mainmorda.utils;

/**
 * User: ivannik
 * Date: 16.08.2014
 */
public class LinkUtils {
    public static String normalizeUrl(String url, String protocol) {
        if (url.startsWith("//")) {
            url = protocol + ":" + url;
        }
        return url;
    }
}
