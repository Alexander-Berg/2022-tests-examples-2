package ru.yandex.autotests.mordabackend.actions;

import org.apache.http.impl.cookie.BasicClientCookie;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.client.ClientUtils;
import ru.yandex.autotests.mordabackend.http.TuneYandexRu;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.net.URI;

import static ru.yandex.autotests.utils.morda.url.UrlManager.encode;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.05.14
 */
public class TuneActions extends AbstractActions {
    private static final URI TUNE_URL = URI.create("http://tune.yandex.ru");

    public TuneActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public void setRegion(Region region) {
        BasicClientCookie yandexGidDomain = new BasicClientCookie("yandex_gid", region.getRegionId());
        yandexGidDomain.setDomain(".yandex" + region.getDomain());
        ClientUtils.getCookieStore(client).addCookie(yandexGidDomain);
        BasicClientCookie yandexGidRu = new BasicClientCookie("yandex_gid", region.getRegionId());
        yandexGidRu.setDomain(".yandex.ru");
        ClientUtils.getCookieStore(client).addCookie(yandexGidRu);
    }

    public void setRegion(String domain, int region) {
        String id = String.valueOf(region);
        BasicClientCookie yandexGidDomain = new BasicClientCookie("yandex_gid", id);
        yandexGidDomain.setDomain(".yandex" + domain);
        ClientUtils.getCookieStore(client).addCookie(yandexGidDomain);
        BasicClientCookie yandexGidRu = new BasicClientCookie("yandex_gid", domain);
        yandexGidRu.setDomain(".yandex.ru");
        ClientUtils.getCookieStore(client).addCookie(yandexGidRu);
    }

    public void setLanguage(String sk, Language lang, URI retpath) {
        TuneYandexRu.apiLangV11SaveXml(client, TUNE_URL)
                .get(sk, lang.getValue(), encode(retpath.toString())).close();
    }

}
