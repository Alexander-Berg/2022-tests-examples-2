package ru.yandex.autotests.mordabackend.actions;

import org.apache.commons.lang3.StringUtils;
import org.glassfish.jersey.message.internal.MessageBodyProviderNotFoundException;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.mordabackend.http.WwwRcYandexRu;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;

import javax.ws.rs.client.Client;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.05.14
 */
public class CleanvarsActions extends AbstractActions {

    public CleanvarsActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public String getAsString(UserAgent userAgent, List<CleanvarsBlock> cleanvarsBlocks) {
        return getAsString(null, userAgent.getValue(), null, null, cleanvarsBlocks, null);
    }

    public Cleanvars get() {
        return get(null, null, null, null, null, null);
    }

    public Cleanvars get(UserAgent userAgent) {
        return get(null, userAgent, null, null, null, null);
    }

    public Cleanvars get(UserAgent userAgent, List<CleanvarsBlock> cleanvarsBlocks) {
        return get(null, userAgent, null, null, cleanvarsBlocks, null);
    }

    public Cleanvars getWithCounters(UserAgent userAgent, List<CleanvarsBlock> cleanvarsBlocks) {
        return get(null, userAgent, null, null, cleanvarsBlocks, "1");
    }

    public Cleanvars get(UserAgent userAgent, String xForwardedFor, List<CleanvarsBlock> cleanvarsBlocks) {
        return get(null, userAgent, xForwardedFor, null, cleanvarsBlocks, null);
    }

    public Cleanvars get(CookieHeader cookieHeader) {
        return get(cookieHeader, null, null, null, null, null);
    }

    public Cleanvars get(CookieHeader cookieHeader, UserAgent userAgent) {
        return get(cookieHeader, userAgent, null, null, null, null);
    }

    public Cleanvars get(CookieHeader cookieHeader, UserAgent userAgent, List<CleanvarsBlock> cleanvarsBlocks) {
        return get(cookieHeader, userAgent, null, null, cleanvarsBlocks, null);
    }

    public Cleanvars get(CookieHeader cookieHeader, UserAgent userAgent, String xForwardedFor) {
        return get(cookieHeader, userAgent, xForwardedFor, null, null, null);
    }

    public Cleanvars get(CookieHeader cookieHeader, UserAgent userAgent, String xForwardedFor,
                         String referer, List<CleanvarsBlock> blocks, String forcecounters)
    {
        return get(cookieHeader, userAgent == null ? null : userAgent.getValue(),
                xForwardedFor, referer, blocks, forcecounters, true);
    }

    public Cleanvars get(CookieHeader cookieHeader, String userAgent, String xForwardedFor,
                         String referer, List<CleanvarsBlock> blocks, String forcecounters, boolean notUsed)
    {
        try {
            return getImpl(cookieHeader, userAgent, xForwardedFor, referer, blocks, forcecounters);
        } catch (MessageBodyProviderNotFoundException e) {
            try {
                return getImpl(cookieHeader, userAgent, xForwardedFor, referer, blocks, forcecounters);
            } catch (MessageBodyProviderNotFoundException e2) {
                return getImpl(cookieHeader, userAgent, xForwardedFor, referer, blocks, forcecounters);
            }
        }
    }

    private Cleanvars getImpl(CookieHeader cookieHeader, String userAgent, String xForwardedFor,
                              String referer, List<CleanvarsBlock> blocks, String forcecounters) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .getAsJson(
                        (blocks == null || blocks.size() == 0) ? "1" : "^" + StringUtils.join(blocks, "$|^") + "$",
                        forcecounters,
                        userAgent,
                        cookieHeader == null ? null : cookieHeader.toString(),
                        xForwardedFor,
                        referer,
                        Cleanvars.class
                );
    }

    private String getAsString(CookieHeader cookieHeader, String userAgent, String xForwardedFor,
                              String referer, List<CleanvarsBlock> blocks, String forcecounters) {
        return WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .getAsJson(
                        (blocks == null || blocks.size() == 0) ? "1" : "^" + StringUtils.join(blocks, "$|^") + "$",
                        forcecounters,
                        userAgent,
                        cookieHeader == null ? null : cookieHeader.toString(),
                        xForwardedFor,
                        referer,
                        String.class
                );
    }

    public void setLanguage(String lang, String sk) {
        WwwRcYandexRu.root(client, mordaClient.getMordaHost())
                .get(lang, sk).close();
    }
}
