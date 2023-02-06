package ru.yandex.autotests.morda.utils.cookie.parsers.y;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/15
 */
public class YCookieParser {

    private static List<String> getYCookieParts(String cookie) {
        if (cookie == null || cookie.isEmpty()) {
            return new ArrayList<>();
        }

        return Arrays.asList(cookie.split("#"));
    }

    public static List<YpCookieValue> parseYpCookie(String cookie) {
        return getYCookieParts(cookie).stream().map(YpCookieValue::new).collect(Collectors.toList());
    }

    public static Map<String, YpCookieValue> parseYpCookieToMap(String cookie) {
        return parseYpCookie(cookie).stream().collect(Collectors.toMap(YpCookieValue::getName, Function.identity()));
    }

    public static List<YsCookieValue> parseYsCookie(String cookie) {
        return getYCookieParts(cookie).stream().map(YsCookieValue::new).collect(Collectors.toList());
    }

    public static Map<String, YsCookieValue> parseYsCookieToMap(String cookie) {
        return parseYsCookie(cookie).stream().collect(Collectors.toMap(YsCookieValue::getName, Function.identity()));
    }

}
