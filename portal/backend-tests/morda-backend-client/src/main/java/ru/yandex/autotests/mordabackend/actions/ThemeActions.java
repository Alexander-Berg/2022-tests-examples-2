package ru.yandex.autotests.mordabackend.actions;

import org.glassfish.jersey.message.internal.MessageBodyProviderNotFoundException;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.mordabackend.http.WwwRcYandexRu;

import javax.ws.rs.client.Client;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.05.14
 */
public class ThemeActions extends AbstractActions {

    public ThemeActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public void set(String themeId, String sk) {
        WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .themes()
                .themeId(themeId)
                .set()
                .get(sk).close();
    }

    public Cleanvars choose(String themeId) {
        return choose(themeId, new CookieHeader());
    }

    public Cleanvars choose(String themeId, CookieHeader cookieHeader) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .themes()
                .themeId(themeId)
                .getAsJson(cookieHeader.toString(), Cleanvars.class);
    }

    public Cleanvars getCatalog() {
        try {
            return WwwRcYandexRu.root(client, mordaClient.getMordaHost()).themes().getAsJson(Cleanvars.class);
        } catch (MessageBodyProviderNotFoundException e) {
            try {
                return WwwRcYandexRu.root(client, mordaClient.getMordaHost()).themes().getAsJson(Cleanvars.class);
            } catch (MessageBodyProviderNotFoundException e1) {
                return WwwRcYandexRu.root(client, mordaClient.getMordaHost()).themes().getAsJson(Cleanvars.class);
            }
        }
    }

    public Cleanvars getCatalog(CookieHeader cookieHeader) {
        try {
            return WwwRcYandexRu.root(client, mordaClient.getMordaHost()).themes()
                    .getAsJson(cookieHeader.toString(), Cleanvars.class);
        } catch (MessageBodyProviderNotFoundException e) {
            return WwwRcYandexRu.root(client, mordaClient.getMordaHost()).themes()
                    .getAsJson(cookieHeader.toString(), Cleanvars.class);
        }
    }


    public Cleanvars setFootball(String themeId) {
        return setFootball(themeId, new CookieHeader());
    }

    public Cleanvars setFootball(String themeId, CookieHeader cookieHeader) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .football(themeId)
                .getAsJson(cookieHeader.toString(), Cleanvars.class);
    }

}
