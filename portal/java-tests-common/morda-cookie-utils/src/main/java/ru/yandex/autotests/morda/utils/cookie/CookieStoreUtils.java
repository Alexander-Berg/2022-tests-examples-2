package ru.yandex.autotests.morda.utils.cookie;

import org.apache.http.client.CookieStore;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.cookie.BasicClientCookie;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08/04/15
 */
class CookieStoreUtils {

    public static Cookie getCookieNamed(CookieStore cookieStore, String name, String domain) {
        Optional<Cookie> result = cookieStore.getCookies().stream().filter(
                (cookie) -> cookie.getName().equals(name) && cookie.getDomain().equals(domain)
        ).findFirst();

        return result.isPresent()
                ? result.get()
                : null;
    }

    public static List<Cookie> getCookies(CookieStore cookieStore) {
        return cookieStore.getCookies();
    }

    public static void addCookie(CookieStore cookieStore, String name, String value, String domain) {
        BasicClientCookie cookie = new BasicClientCookie(name, value);
        cookie.setDomain(domain);
        addCookie(cookieStore, cookie);
    }

    public static void addCookie(CookieStore cookieStore, Cookie cookie) {
        cookieStore.addCookie(cookie);
    }

    public static void deleteCookieNamed(CookieStore cookieStore, String name) {
        List<Cookie> cookies = getCookies(cookieStore).stream().filter((cookie) -> !cookie.getName().equals(name))
                .collect(Collectors.toList());

        deleteAllCookies(cookieStore);

        cookies.forEach(cookieStore::addCookie);
    }

    public static void deleteCookie(CookieStore cookieStore, Cookie cookieToDelete) {
        List<Cookie> cookies = getCookies(cookieStore).stream().filter((cookie) -> !cookie.equals(cookieToDelete))
                .collect(Collectors.toList());

        deleteAllCookies(cookieStore);

        cookies.forEach(cookieStore::addCookie);
    }

    public static void deleteAllCookies(CookieStore cookieStore) {
        cookieStore.clear();
    }
}
