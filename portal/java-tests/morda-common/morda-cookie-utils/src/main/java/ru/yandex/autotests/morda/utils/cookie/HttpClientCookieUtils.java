package ru.yandex.autotests.morda.utils.cookie;

import org.apache.http.client.CookieStore;
import org.apache.http.client.HttpClient;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.client.CloseableHttpClient;

import java.lang.reflect.Field;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/12/14
 */
public class HttpClientCookieUtils extends MordaCookieUtils<Cookie> {

    private HttpClient httpClient;

    public HttpClientCookieUtils(HttpClient httpClient) {
        this.httpClient = httpClient;
    }

    private CookieStore getCookieStore() {
        if (httpClient instanceof CloseableHttpClient) {
            try {
                Class<?> c = Class.forName("org.apache.http.impl.client.InternalHttpClient");
                Field field = c.getDeclaredField("cookieStore");
                field.setAccessible(true);
                return (CookieStore) field.get(httpClient);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }

        throw new IllegalArgumentException("Expected CloseableHttpClient");
    }

    @Override
    public Cookie getCookieNamed(String name, String domain) {
        return CookieStoreUtils.getCookieNamed(getCookieStore(), name, domain);
    }

    @Override
    public List<Cookie> getCookies() {
        return CookieStoreUtils.getCookies(getCookieStore());
    }

    @Override
    public void addCookie(String name, String value, String domain) {
        CookieStoreUtils.addCookie(getCookieStore(), name, value, domain);
    }

    @Override
    public void addCookie(Cookie cookie) {
        CookieStoreUtils.addCookie(getCookieStore(), cookie);
    }

    @Override
    public void deleteCookieNamed(String name) {
        CookieStoreUtils.deleteCookieNamed(getCookieStore(), name);
    }

    @Override
    public void deleteCookie(Cookie cookie) {
        CookieStoreUtils.deleteCookie(getCookieStore(), cookie);
    }

    @Override
    public void deleteAllCookies() {
        CookieStoreUtils.deleteAllCookies(getCookieStore());
    }

    @Override
    public String getCookieValue(Cookie cookie) {
        return cookie != null ? cookie.getValue() : null;
    }
}
