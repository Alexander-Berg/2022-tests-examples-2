package ru.yandex.autotests.mordabackend.headers;

import org.apache.commons.lang.StringUtils;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.02.14
 */
public class CookieHeader {
    private List<Cookie> cookies;

    public CookieHeader() {
        this.cookies = new ArrayList<>();
    }

    public CookieHeader(Cookie... cookies) {
        this.cookies = new ArrayList<>(Arrays.asList(cookies));
    }

    public CookieHeader(List<Cookie> cookies) {
        this.cookies = cookies;
    }

    public void addCookie(CookieName cookieName, String value) {
        addCookies(Arrays.asList(new Cookie(cookieName, value)));
    }

    public void addCookies(Cookie... cookies) {
        addCookies(Arrays.asList(cookies));
    }

    public void addCookies(List<Cookie> cookies) {
        this.cookies.addAll(cookies);
    }

    @Override
    public String toString() {
        if (cookies.size() == 0) {
            return null;
        }
        return StringUtils.join(cookies, "; ");
    }
}
