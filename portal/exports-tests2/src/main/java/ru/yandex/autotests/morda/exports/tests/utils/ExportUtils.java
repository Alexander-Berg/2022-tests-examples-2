package ru.yandex.autotests.morda.exports.tests.utils;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 11.02.14
 */
public class ExportUtils {
    public static String normalizeUrl(String url) {
        if (url.startsWith("//")) {
            return "http:" + url;
        }
        return url;
    }
}
