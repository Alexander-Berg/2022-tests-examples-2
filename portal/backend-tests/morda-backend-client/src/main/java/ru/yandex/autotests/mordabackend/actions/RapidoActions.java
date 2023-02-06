package ru.yandex.autotests.mordabackend.actions;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.mordabackend.http.WwwRcYandexRu;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.05.14
 */
public class RapidoActions extends AbstractActions {

    public RapidoActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public Cleanvars get(String block) {
        return get(block, null, null, null, null);
    }

    public Cleanvars get(String block, UserAgent userAgent) {
        return get(block, null, userAgent, null, null);
    }

    public Cleanvars get(String block, UserAgent userAgent, String xForwardedFor) {
        return get(block, null, userAgent, xForwardedFor, null);
    }

    public Cleanvars get(String block, CookieHeader cookieHeader) {
        return get(block, cookieHeader, null, null, null);
    }

    public Cleanvars get(String block, CookieHeader cookieHeader, UserAgent userAgent) {
        return get(block, cookieHeader, userAgent, null, null);
    }

    public Cleanvars get(String block, CookieHeader cookieHeader, UserAgent userAgent, String xForwardedFor) {
        return get(block, cookieHeader, userAgent, xForwardedFor, null);
    }

    public Cleanvars get(String block, CookieHeader cookieHeader, UserAgent userAgent, String xForwardedFor,
                         String referer) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .instant()
                .blockBlock(block)
                .getAsJson(
                        userAgent == null ? null : userAgent.getValue(),
                        cookieHeader == null ? null : cookieHeader.toString(),
                        xForwardedFor,
                        referer,
                        Cleanvars.class
                );
    }

    public Response getResponse(String block, CookieHeader cookieHeader, UserAgent userAgent, String xForwardedFor,
                                String referer) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .instant()
                .blockBlock(block)
                .get(
                        userAgent == null ? null : userAgent.getValue(),
                        cookieHeader == null ? null : cookieHeader.toString(),
                        xForwardedFor,
                        referer
                );
    }

    public Cleanvars getAll(CookieHeader cookieHeader, UserAgent userAgent, String xForwardedFor,
                         String referer) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .instant()
                .all()
                .getAsJson(
                        userAgent == null ? null : userAgent.getValue(),
                        cookieHeader == null ? null : cookieHeader.toString(),
                        xForwardedFor,
                        referer,
                        Cleanvars.class
                );
    }

    public Response getAllResponse(CookieHeader cookieHeader, UserAgent userAgent, String xForwardedFor,
                                String referer) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .instant()
                .all()
                .get(
                        userAgent == null ? null : userAgent.getValue(),
                        cookieHeader == null ? null : cookieHeader.toString(),
                        xForwardedFor,
                        referer
                );
    }

    public void setLanguage(String lang, String sk) {
        WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .get(lang, sk).close();
    }
}
