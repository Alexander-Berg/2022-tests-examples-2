package ru.yandex.autotests.mainmorda.data;

import ch.lambdaj.function.convert.Converter;
import org.hamcrest.Matcher;
import org.openqa.selenium.Dimension;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.utils.ServiceAndDomain;
import ru.yandex.autotests.mainmorda.utils.TabInfo;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.*;

import static ch.lambdaj.Lambda.convert;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mainmorda.utils.ServiceAndDomain.snd;
import static ru.yandex.autotests.mainmorda.utils.TabInfo.TabsInfoBuilder.tabInfo;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.MordaExport;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.ServicesV122EntryMatcher.with;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: eoff
 * Date: 03.12.12
 */
public class TabsData {
    public static final Properties CONFIG = new Properties();

    protected static List<TabInfo> getBetaTabs(MordaExport<ServicesV122Entry> export,
                                                           String ... tabIds) {
        return convert(exports(export, domain(CONFIG.getBaseDomain()), with().tabs(greaterThan(0)),
                with().tabsMore(0), with().id(isIn(tabIds))), new Converter<ServicesV122Entry, TabInfo>() {
            @Override
            public TabInfo convert(ServicesV122Entry from) {
                return tabInfo(from, ENCODED_REQUEST)
                        .withRequest(BETA_REQUESTS.get(snd(CONFIG.getBaseDomain(), from.getId())))
                        .build();
            }
        });
    }

    protected static List<TabInfo> getDefaultTabsListWithout(MordaExport<ServicesV122Entry> export,
                                                           String ... excludeIds) {
        return convert(exports(export, domain(CONFIG.getBaseDomain()),
                with().tabs(allOf(greaterThan(0), lessThan(10))), with().tabsMore(0), with().id(not(isIn(excludeIds)))), TABS_CONVERTER);
    }

    protected static List<TabInfo> getDefaultTabsList(MordaExport<ServicesV122Entry> export) {
        return convert(exports(export, domain(CONFIG.getBaseDomain()),
                with().tabs(allOf(greaterThan(0), lessThan(10))), with().tabsMore(0)), TABS_CONVERTER);
    }

    protected static List<TabInfo> getDefaultMoreTabsList(MordaExport<ServicesV122Entry> export) {
        return convert(exports(export, domain(CONFIG.getBaseDomain()),
                with().tabs(anyOf(equalTo(0), greaterThanOrEqualTo(10))), with().tabsMore(greaterThan(0))), TABS_CONVERTER);
    }

    protected static List<TabInfo> getMoreTabsListWithout(MordaExport<ServicesV122Entry> export,
                                                          String... excludeIds) {
        return convert(exports(export, domain(CONFIG.getBaseDomain()),
                with().tabs(anyOf(equalTo(0), greaterThanOrEqualTo(10))), with().tabsMore(greaterThan(0)),
                with().id(not(isIn(excludeIds)))), TABS_CONVERTER);
    }

    protected static List<TabInfo> getHiddenTabsList(MordaExport<ServicesV122Entry> export) {
        return convert(exports(export, domain(CONFIG.getBaseDomain()),
                        with().tabs(allOf(greaterThan(0), lessThan(10))), with().tabsMore(greaterThan(0))), TABS_CONVERTER);
    }

    public static final String REQUEST = "javascript здесь";
    public static final String ENCODED_REQUEST = UrlManager.encodeRequest(REQUEST);

    private static final Converter<ServicesV122Entry, TabInfo> TABS_CONVERTER = new Converter<ServicesV122Entry, TabInfo>() {
        @Override
        public TabInfo convert(ServicesV122Entry from) {
            return tabInfo(from, ENCODED_REQUEST)
                    .withHref(SPECIAL_HREFS.get(snd(CONFIG.getBaseDomain(), from.getId())))
                    .build();
        }
    };

    protected static Map<ServiceAndDomain, String> SPECIAL_HREFS = new HashMap<ServiceAndDomain, String>(){{
        put(snd(RU, "market"), "https://market.yandex.ru/?clid=505");
        put(snd(UA, "market"), "https://market.yandex.ua/?clid=505");
        put(snd(KZ, "market"), "https://market.yandex.kz/?clid=505");
        put(snd(BY, "market"), "https://market.yandex.by/?clid=505");

        put(snd(RU, "traffic"), CONFIG.getProtocol() + "://maps.yandex.ru/moscow_traffic");
        put(snd(UA, "traffic"), CONFIG.getProtocol() + "://maps.yandex.ua/kiev_traffic");
        put(snd(KZ, "traffic"), CONFIG.getProtocol() + "://maps.yandex.ru/astana_traffic");
        put(snd(BY, "traffic"), CONFIG.getProtocol() + "://maps.yandex.ru/minsk_traffic");
    }};

    protected static Map<ServiceAndDomain, String> SPECIAL_REQUEST_PATTERN =
            new HashMap<ServiceAndDomain, String>(){{
        put(snd(RU, "slovari"),
                "http://slovari.yandex.ru/" + ENCODED_REQUEST + "/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4");
        put(snd(UA, "slovari"),
                "http://slovari.yandex.ua/" + ENCODED_REQUEST + "/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4");
        put(snd(KZ, "slovari"),
                "http://slovari.yandex.kz/" + ENCODED_REQUEST + "/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4");
        put(snd(BY, "slovari"),
                "http://slovari.yandex.ru/" + ENCODED_REQUEST + "/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4");

        put(snd(RU, "afisha"), "https://afisha.yandex.ru/msk/search/?text=" + ENCODED_REQUEST);
        put(snd(UA, "afisha"), "https://afisha.yandex.ua/kyv/search/?text=" + ENCODED_REQUEST);
        put(snd(KZ, "afisha"), "https://afisha.yandex.kz/ast/search/?text=" + ENCODED_REQUEST);
        put(snd(BY, "afisha"), "https://afisha.yandex.by/mnk/search/?text=" + ENCODED_REQUEST);

        put(snd(RU, "yaca"), "http://yaca.yandex.ru/yca?yaca=1&text=" + ENCODED_REQUEST);
        put(snd(UA, "yaca"), "http://yaca.yandex.ua/yca?yaca=1&text=" + ENCODED_REQUEST);
        put(snd(KZ, "yaca"), "http://yaca.yandex.kz/yca?yaca=1&text=" + ENCODED_REQUEST);
        put(snd(BY, "yaca"), "http://yaca.yandex.by/yca?yaca=1&text=" + ENCODED_REQUEST);

        put(snd(RU, "disk"), "https://disk.yandex.ru/?auth=1&" +
                "retpath=https%3A%2F%2Fdisk.yandex.ru%2F%3Fsource%3Dservices-main");
        put(snd(UA, "disk"), "https://disk.yandex.ua/?auth=1&" +
                "retpath=https%3A%2F%2Fdisk.yandex.ua%2F%3Fsource%3Dservices-main");
        put(snd(KZ, "disk"), "https://disk.yandex.kz/?auth=1&" +
                "retpath=https%3A%2F%2Fdisk.yandex.kz%2F%3Fsource%3Dservices-main");
        put(snd(BY, "disk"), "https://disk.yandex.ru/?auth=1&" +
                "retpath=https%3A%2F%2Fdisk.yandex.by%2F%3Fsource%3Dservices-main");
    }};

    protected static Map<ServiceAndDomain, String> BETA_REQUESTS = new HashMap<ServiceAndDomain, String>(){{
        put(snd(RU, "images"), "http://beta.yandex.ru/images/search?text=" + ENCODED_REQUEST);
        put(snd(UA, "images"), "http://beta.yandex.ua/images/search?text=" + ENCODED_REQUEST);
        put(snd(KZ, "images"), "http://beta.yandex.kz/images/search?text=" + ENCODED_REQUEST);
        put(snd(BY, "images"), "http://beta.yandex.by/images/search?text=" + ENCODED_REQUEST);

        put(snd(RU, "video"), "http://beta.yandex.ru/video/search?text=" + ENCODED_REQUEST);
        put(snd(UA, "video"), "http://beta.yandex.ua/video/search?text=" + ENCODED_REQUEST);
        put(snd(KZ, "video"), "http://beta.yandex.kz/video/search?text=" + ENCODED_REQUEST);
        put(snd(BY, "video"), "http://beta.yandex.by/video/search?text=" + ENCODED_REQUEST);
    }};

    public static final String FAMILY_SEARCH_URL = CONFIG.getBaseURL().replace("www", "family");
    public static final Matcher<String> FAMILY_TABS_PARAMETER_MATCHER =
            anyOf(containsString("family=1"), containsString("family%3D1"));

    public static final Dimension SIZE_BIG = new Dimension(1500, 600);
    public static final Dimension SIZE_AVG = new Dimension(1000, 600);
    public static final Dimension SIZE_SMALL = new Dimension(900, 600);
    public static final Dimension SIZE_EXTRA_SMALL = new Dimension(700, 600);

    public static final List<TabInfo> MAIN_TABS_DEFAULT = getDefaultTabsListWithout(SERVICES_V12_2, "search");
    public static final List<TabInfo> TABS_HIDDEN = getHiddenTabsList(SERVICES_V12_2);
    public static final List<TabInfo> MAIN_TABS = new ArrayList<TabInfo>(MAIN_TABS_DEFAULT) {{
        addAll(TABS_HIDDEN);
    }};

    public static final List<TabInfo> BETA_TABS = getBetaTabs(SERVICES_V12_2, "images", "video");

    public static final List<TabInfo> FAMILY_TABS =
            getDefaultTabsListWithout(SERVICES_V12_2, "search", "maps", "slovari");

    public static final List<TabInfo> MORE_TABS_DEFAULT = getDefaultMoreTabsList(SERVICES_V12_2);
    public static final List<TabInfo> MORE_TABS = new ArrayList<TabInfo>(MORE_TABS_DEFAULT) {{
        addAll(TABS_HIDDEN);
    }};

    public static final List<TabInfo> MAIN_TABS_EXTRA_SMALL = new ArrayList<>();

    public static final List<TabInfo> MAIN_TABS_SMALL = new ArrayList<TabInfo>() {{
        add(TABS_HIDDEN.get(0));
    }};

    public static final List<TabInfo> MAIN_TABS_AVG = TABS_HIDDEN.subList(0, 1);

    public static final List<TabInfo> MAIN_TABS_FULL = TABS_HIDDEN;

    public static final List<TabInfo> MORE_TABS_EXTRA_SMALL = new ArrayList<>(TABS_HIDDEN);

    public static final List<TabInfo> MORE_TABS_SMALL = new ArrayList<TabInfo>(TABS_HIDDEN) {{
        remove(TABS_HIDDEN.get(0));
    }};

    public static final List<TabInfo> MORE_TABS_AVG = TABS_HIDDEN.subList(1, TABS_HIDDEN.size());

    public static final List<TabInfo> MORE_TABS_FULL = Collections.emptyList();

    public static final List<TabInfo> FAMILY_MORE_TABS;
    static {
        if (CONFIG.getMode().equals(Mode.WIDGET)) {
            FAMILY_MORE_TABS =
                    getMoreTabsListWithout(SERVICES_V12_2,
                            "traffic", "yaca", "uslugi", "mail", "gorod",
                            "money");
        } else {
            FAMILY_MORE_TABS =
                    getMoreTabsListWithout(SERVICES_V12_2,
                            "traffic", "yaca", "uslugi", "gorod",
                            "money");
        }
    }

    public static final List<TabInfo> TABS_PAGE_404 = getDefaultTabsList(SERVICES_V12_2);
}