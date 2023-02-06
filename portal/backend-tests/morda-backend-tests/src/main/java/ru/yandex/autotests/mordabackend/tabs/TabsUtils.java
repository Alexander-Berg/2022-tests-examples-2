package ru.yandex.autotests.mordabackend.tabs;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.MapsEntry;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesTabsEntry;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.*;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.mordaexportslib.matchers.MordatypeMatcher.mordatype;
import static ru.yandex.autotests.utils.morda.region.Region.*;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.05.14
 */
public class TabsUtils {
    private static final Properties CONFIG = new Properties();

    public static final String SEARCH_REQUEST = "test_request";

    public static final Map<Region, String> SPECIAL_TRAFFIC_URLS = new HashMap<Region, String>(){{
        put(ASTANA, "https://yandex.ru/maps/163/astana/probki");
        put(KIEV, "https://yandex.ua/maps/143/kyiv/probki");
        put(MINSK, "https://yandex.ru/maps/157/minsk/probki");
        put(MOSCOW, "https://yandex.ru/maps/213/moscow/probki");
    }};

    public static List<ServicesV122Entry> getTabsServices(Domain d, UserAgent userAgent) {
        List<ServicesV122Entry> services = exports(SERVICES_V12_2, domain(d),
                userAgent.isMobile() ?
                        allOf(having(on(ServicesV122Entry.class).getTabsTouch(), not(equalTo(0))),
                                having(on(ServicesV122Entry.class).getIphone(), not(equalTo(0)))) :
                        having(on(ServicesV122Entry.class).getTabs(), allOf(not(equalTo(0)), lessThan(10)))
        );
        List<ServicesV122Entry> data = new ArrayList<>();
        for (ServicesV122Entry entry : services) {
            data.add(prepareEntry(entry));
        }
        return data;
    }

    public static List<ServicesV122Entry> getTabsMoreServices(Domain d) {
        List<ServicesV122Entry> services = exports(SERVICES_V12_2, domain(d),
                having(on(ServicesV122Entry.class).getTabsMore(), not(equalTo(0)))
        );
        List<ServicesV122Entry> data = new ArrayList<>();
        for (ServicesV122Entry entry : services) {
            data.add(prepareEntry(entry));
        }
        return data;
    }


    public static Matcher<String> getUrlMatcher(ServicesV122Entry entry, UserAgent userAgent) {
        switch (entry.getId()) {
            case "market":
                return userAgent.isMobile() ?
                        startsWith(getTouchHref(entry)) :
                        startsWith(entry.getHref().replace("clid=506", "clid=505").replace("clid=691", "clid=505"));
            case "tv":
                return userAgent.isMobile() ?
                        startsWith("https:" + getTouchHref(entry)) :
                        anyOf(startsWith(entry.getHref()), startsWith("https:" + entry.getHref()));
        }
        return userAgent.isMobile() ?
                startsWith(getTouchHref(entry)) :
                startsWith(entry.getHref());
    }


    public static Matcher<String> getHrefMatcher(ServicesV122Entry entry, Region region, Language language, UserAgent userAgent) {
        System.out.println(entry);
        switch (entry.getId()) {
            case "market":
                return anyOf(
                        startsWith(entry.getHref().replace("clid=506", "clid=505").replace("clid=691", "clid=505")),
                        equalTo(entry.getTouch())
                );
            case "traffic":
                return SPECIAL_TRAFFIC_URLS.containsKey(region) ? equalTo(SPECIAL_TRAFFIC_URLS.get(region)) :
                        startsWith(entry.getSearch());
            case "afisha":
                return startsWith(entry.getHref());
            case "tv":
                return anyOf(startsWith(entry.getHref()), startsWith("https:" + entry.getHref()));
            case "maps":
                return startsWith(export(MAPS, geo(region.getRegionIdInt()), having(on(MapsEntry.class).getUrl(),
                        notNullValue()), mordatype(region.getDomain().getValue().replace(".", "")), lang(language))
                        .getUrl());
        }
        return userAgent.isMobile() && entry.getTouch() != null && !entry.getTouch().equals("") ?
                startsWith(entry.getTouch()) :
                startsWith(entry.getHref());
    }

    private static String getTouchHref(ServicesV122Entry entry) {
        if (entry.getTouch() != null && !entry.getTouch().equals("")) {
            return entry.getTouch();
        } else if (entry.getPda() != null && !entry.getPda().equals("")) {
            return entry.getPda();
        } else {
            return entry.getHref();
        }
    }

    private static ServicesV122Entry prepareEntry(ServicesV122Entry entry) {
        switch (entry.getId()) {
            case "market":
                entry.setHref(entry.getHref().replace("clid=506", "clid=505"));
                entry.setHref(entry.getHref().replace("clid=691", "clid=505"));
                break;
            case "traffic":
                entry.setHref(entry.getSearch());
                break;
        }
        return entry;
    }

    public static String withRequest(String searchUrl, String request) {
        if (searchUrl.contains("?")) {
            if (searchUrl.endsWith("=")) {
                return searchUrl + encodeRequest(request);
            } else {
                return searchUrl + "&text=" + encodeRequest(request);
            }
        } else {
            return searchUrl + "?text=" + encodeRequest(request);
        }
    }

    public static String getComTrUrl(ServicesTabsEntry entry) {
        switch (entry.getId()) {
            case "market":
                return entry.getUrl().replace("clid=691", "clid=505").replace("\\?", "?redirect=1");
        }
        return entry.getUrl();
    }
}
