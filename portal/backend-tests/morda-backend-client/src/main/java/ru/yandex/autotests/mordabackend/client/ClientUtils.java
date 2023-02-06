package ru.yandex.autotests.mordabackend.client;

import org.apache.http.client.CookieStore;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.cookie.BasicClientCookie;
import org.glassfish.jersey.client.ClientConfig;
import org.glassfish.jersey.client.spi.Connector;

import javax.ws.rs.client.Client;
import java.lang.reflect.Method;
import java.util.Date;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.selectFirst;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.06.14
 */
public class ClientUtils {
    public static void addCookie(Client client, String name, String value, String domain) {
        BasicClientCookie cookie = new BasicClientCookie(name, value);
        cookie.setDomain(domain);
        getCookieStore(client).addCookie(cookie);
    }

    public static void removeCookie(Client client, String name, String domain) {
        BasicClientCookie cookie = new BasicClientCookie(name, null);
        cookie.setExpiryDate(new Date(0));
        cookie.setDomain(domain);
        getCookieStore(client).addCookie(cookie);
    }

    public static String getCookieValue(Client client, String name, String domain) {
        Cookie c = selectFirst(getCookieStore(client).getCookies(),
                allOf(
                        having(on(Cookie.class).getName(), equalTo(name)),
                        having(on(Cookie.class).getDomain(), equalTo(domain))
                ));
        return c == null ? null : c.getValue();
    }

    public static CookieStore getCookieStore(Client client) {
        ClientConfig clientConfig = ((ClientConfig) client.getConfiguration());
        Connector connector = clientConfig.getConnector();
        try {
            Class<?> c = Class.forName("org.glassfish.jersey.apache.connector.ApacheConnector");
            Method method = c.getDeclaredMethod("getCookieStore");
            method.setAccessible(true);
            return (CookieStore) method.invoke(connector);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
