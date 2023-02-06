package ru.yandex.autotests.morda.utils.cookie;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08/04/15
 */
public interface CookieUtils<E> {
    E getCookieNamed(String name, String domain);

    List<E> getCookies();

    void addCookie(String name, String value, String domain);

    void addCookie(E cookie);

    void deleteCookieNamed(String name);

    void deleteCookie(E cookie);

    void deleteAllCookies();

    String getCookieValue(E cookie);

}
