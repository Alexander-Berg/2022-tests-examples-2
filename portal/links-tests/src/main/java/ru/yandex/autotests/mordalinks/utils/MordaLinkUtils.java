package ru.yandex.autotests.mordalinks.utils;

import org.apache.log4j.Logger;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordalinks.Properties;
import ru.yandex.autotests.mordalinks.beans.MordaLink;
import ru.yandex.autotests.mordalinks.beans.MordaLinkList;
import ru.yandex.autotests.mordalinks.beans.MordaLinksCount;
import ru.yandex.autotests.mordalinks.beans.Url;
import ru.yandex.autotests.mordalinks.http.PortalHazeYandexNet;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import javax.ws.rs.WebApplicationException;
import java.util.List;

import static ru.yandex.autotests.mordalinks.utils.NormalizeUtils.normalizeOnAdd;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.05.14
 */
public class MordaLinkUtils {

    private static final Properties CONFIG = new Properties();
    private static final Logger LOG = Logger.getLogger(MordaLinkUtils.class);

    public static boolean addLink(MordaLink link) {
        try {
            link.setHref(normalizeOnAdd(link.getHref()));
            new PortalHazeYandexNet.ApiV1Links(MordaClient.getJsonEnabledClient(), CONFIG.getLinksHost())
                    .postJson(link, MordaLink.class);
        } catch (WebApplicationException e) {
            return false;
        }
        return true;
    }

    public static List<MordaLink> getAllLinks() {
        return new PortalHazeYandexNet.ApiV1Links(MordaClient.getJsonEnabledClient(), CONFIG.getLinksHost())
                .getAsJson(0, MordaLinkList.class).getData();
    }

    public static MordaLinksCount getChangedLinksCount() {
        String query = "[{\"field\":\"changed\",\"value\":true},{\"field\":\"blocked\",\"value\":false}]";
        return new PortalHazeYandexNet.ApiV1Links(MordaClient.getJsonEnabledClient(), CONFIG.getLinksHost())
                .count()
                .getAsJson(UrlManager.encode(query), MordaLinksCount.class);
    }

    public static void updateLink(String _id, Url url) {
        new PortalHazeYandexNet.ApiV1Links(MordaClient.getJsonEnabledClient(), CONFIG.getLinksHost())
                .linkIdCandidate(_id)
                .putJson(url, Url.class);
    }

    public static void main(String[] args) {
        System.out.println(getChangedLinksCount());
    }
}
