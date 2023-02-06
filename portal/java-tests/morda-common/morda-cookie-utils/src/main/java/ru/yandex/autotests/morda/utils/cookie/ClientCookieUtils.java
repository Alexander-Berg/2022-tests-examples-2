package ru.yandex.autotests.morda.utils.cookie;

import org.apache.http.client.CookieStore;
import org.apache.http.cookie.Cookie;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;

import javax.ws.rs.client.Client;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/12/14
 */
public class ClientCookieUtils extends MordaCookieUtils<Cookie> {

    private Client client;

    public ClientCookieUtils(Client client) {
        this.client = client;
    }

    private CookieStore getCookieStore() {
        return ApacheConnectorProvider.getCookieStore(client);
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
