package ru.yandex.autotests.tuneapitests.utils;

import org.apache.http.client.CookieStore;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.cookie.BasicClientCookie;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;

import javax.ws.rs.client.Client;
import java.util.*;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class SynCookieUtils {

    public static void synKUBRCookies(Client client, String ... cookiesToSyn) {
        Set<String> notSyncedCookies = new HashSet<>(Arrays.asList(cookiesToSyn));
        CookieStore cs = ApacheConnectorProvider.getCookieStore(client);
        for (Cookie c : cs.getCookies()) {
            if (Arrays.asList(cookiesToSyn).contains(c.getName()) && c.getDomain().endsWith(".yandex.ru")) {
                notSyncedCookies.remove(c.getName());
                for (String d : getDomainsToSyn(c.getDomain())) {
                    BasicClientCookie newC = new BasicClientCookie(c.getName(), c.getValue());
                    newC.setDomain(d);
                    newC.setExpiryDate(c.getExpiryDate());
                    newC.setPath(c.getPath());
                    newC.setVersion(c.getVersion());
                    newC.setSecure(c.isSecure());
                    cs.addCookie(newC);
                }
            }
        }
        for (String notSyncedCookie : notSyncedCookies) {
            for (String d : getDomainsToSyn(".yandex.ru")) {
                removeCookie(cs, notSyncedCookie, d);
            }
        }
    }

    private static List<String> getDomainsToSyn(String domain) {
        List<String> domains = new ArrayList<>();
        domains.add(domain.replaceAll("\\.ru$", ".kz"));
        domains.add(domain.replaceAll("\\.ru$", ".ua"));
        domains.add(domain.replaceAll("\\.ru$", ".by"));
        return domains;
    }

    public static void removeCookie(CookieStore cs, String name, String domain) {
        BasicClientCookie cookie = new BasicClientCookie(name, null);
        cookie.setExpiryDate(new Date(0));
        cookie.setDomain(domain);
        cs.addCookie(cookie);
    }
}
