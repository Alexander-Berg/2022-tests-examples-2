package ru.yandex.autotests.mordabackend.utils;

import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import static ru.yandex.autotests.utils.morda.url.DomainManager.getMasterDomain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10.06.14
 */
public class LinkUtils {
    public static void addLink(String href, Region region, boolean auth, Language lang, UserAgent ua) {
        System.out.println("Adding link: " + href);
//        MordaLinkUtils.addLink(
//                new MordaLink()
//                        .withHref(normalizeUrl(href))
//                        .withCond(new MordaConditions()
//                                        .withAuth(auth)
//                                        .withGid(region.getRegionIdInt())
//                                        .withLang(lang != null ? lang.getValue() : null)
//                                        .withUa(ua == null ? null : ua.getMongoId())
//                        )
//        );
    }

    public static String normalizeUrl(String url) {
        if (url.startsWith("//")) {
            url = "https:" + url;
        }
        return url;
    }

    public static Domain getExpectedDomain(Domain domain, UserAgent userAgent) {
        return userAgent.isMobile() ? getMasterDomain(domain) : domain;
    }
}
