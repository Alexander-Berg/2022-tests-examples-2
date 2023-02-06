package ru.yandex.autotests.mordabackend.topnews;

import ch.lambdaj.Lambda;
import ch.lambdaj.function.convert.Converter;
import org.hamcrest.Matcher;
import ru.yandex.autotests.mordabackend.beans.local.LocalBlock;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTab;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordaexportsclient.beans.TopnewsStocksEntry;
import ru.yandex.autotests.utils.morda.data.MordaDate;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.flatten;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.TOPNEWS_STOCKS;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ADANA;
import static ru.yandex.autotests.utils.morda.region.Region.ALANYA;
import static ru.yandex.autotests.utils.morda.region.Region.ALMATY;
import static ru.yandex.autotests.utils.morda.region.Region.ANTALYA;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.BURSA;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.DNEPROPETROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.DUBNA;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.GAZIANTEP;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.IZMIR;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MERSIN;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.UFA;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIVOSTOK;
import static ru.yandex.autotests.utils.morda.region.Region.YAROSLAVL;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17.07.14
 */
public class TopnewsUtils {

    public static final List<Region> TOPNEWS_REGIONS_MAIN = Arrays.asList(
            MOSCOW, KIEV, SANKT_PETERBURG, MINSK, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, DUBNA, ASTANA, ALMATY,
            VLADIVOSTOK, UFA, YAROSLAVL, HARKOV, DNEPROPETROVSK
    );

    public static final List<Region> TOPNEWS_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> TOPNEWS_REGIONS_ALL = new ArrayList<>();

    static {
        TOPNEWS_REGIONS_ALL.addAll(TOPNEWS_REGIONS_MAIN);
    }

    public static Matcher<Integer> getTabsCountMatcher(Region region) {
        if (region.getDomain().equals(KZ)) {
            return equalTo(3);
        }
        return equalTo(2);
    }

    public static List<Integer> getTopnewsStocks(Region region) {
        return flatten(
                convert(
                        extract(
                                exports(TOPNEWS_STOCKS, domain(region.getDomain()), geo(region.getRegionIdInt())),
                                on(TopnewsStocksEntry.class).getStocks()
                        ),
                        new Converter<String, List<Integer>>() {
                            @Override
                            public List<Integer> convert(String s) {
                                return Lambda.convert(s.split(","), new Converter<String, Integer>() {
                                    @Override
                                    public Integer convert(String toInt) {
                                        return Integer.valueOf(toInt.trim());
                                    }
                                });
                            }
                        }
                )
        );
    }

    public static final String SPORT_LINK_PART = "sport.html";
    public static final String SPORT_UK_LINK_PART = "sport.uk.html";
    public static final String WORLD_LINK_PART = "world.html";
    public static final String YANDSEARCH_LINK_PART = "yandsearch";

    public static final String NEWS = "news";
    public static final String REGION = "region";
    public static final String SPORT = "sport";
    public static final String IN_WORLD = "in_world";
    public static final String WORLD = "world";
    public static final String THEME = "theme";

    private static final Map<String, String> NAME_MAP = new HashMap<>();

    static {
        NAME_MAP.put(NEWS, NEWS);
        NAME_MAP.put(REGION, REGION);
        NAME_MAP.put(IN_WORLD, WORLD);
        NAME_MAP.put(SPORT, THEME);
    }

    private static final List<String> TOUCH_ALL_TABS_LIST = Arrays.asList("index", "region", "politics", "society",
            "business", "world", "sport", "incident", "culture", "science", "computers", "auto");

    private static final List<String> TOUCH_NO_REGION_TABS_LIST = Arrays.asList("index", "politics", "society",
            "business", "world", "sport", "incident", "culture", "science", "computers", "auto");

    private static final Map<Domain, List<String>> TABS_REGION_MAP = new HashMap<>();

    static {
        TABS_REGION_MAP.put(Domain.RU, Arrays.asList(NEWS, REGION));
        TABS_REGION_MAP.put(UA, Arrays.asList(NEWS, REGION));
        TABS_REGION_MAP.put(KZ, Arrays.asList(NEWS, IN_WORLD, SPORT));
        TABS_REGION_MAP.put(BY, Arrays.asList(NEWS, IN_WORLD));
    }

    private static final Map<Domain, List<String>> TOUCH_TABS_REGION_MAP = new HashMap<>();

    static {
        TOUCH_TABS_REGION_MAP.put(Domain.RU, TOUCH_ALL_TABS_LIST);
        TOUCH_TABS_REGION_MAP.put(UA, TOUCH_ALL_TABS_LIST);
        TOUCH_TABS_REGION_MAP.put(KZ, Arrays.asList("index", "world", "sport"));
        TOUCH_TABS_REGION_MAP.put(BY, TOUCH_NO_REGION_TABS_LIST);
    }

    public static final int NEWS_NUMBER = 5;

    public static Matcher<String> getFullTimeMatcher(String hiddenTime) throws ParseException {
        final Date localTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(hiddenTime);
        return equalTo(new SimpleDateFormat("HH:mm dd/MM/yyyy").format(localTime));
    }

    public static Matcher<String> getTimeMatcher(String hiddenTime) throws ParseException {
        final Date localTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(hiddenTime);
        return equalTo(new SimpleDateFormat("HH:mm").format(localTime));
    }

    public static Matcher<String> getWDayMatcher(LocalBlock localBlock, Language language) {
        return equalTo(getTranslation(MordaDate.DAY_OF_WEEK.get(localBlock.getWday() + 1), language));
    }

    public static Matcher<String> getMonthMatcher(LocalBlock localBlock, Language language) {
        return equalTo(getTranslation(MordaDate.MONTH_NAME.get(localBlock.getMon() - 1), language));
    }

    public static Matcher<String> getRegionHrefMatcher(ServicesV122Entry servicesV12Entry, Region region,
                                                       UserAgent userAgent) {
        if (userAgent.isMobile() && userAgent.getIsTouch() == 1) {
            return startsWith(servicesV12Entry.getTouch());
        } else if (userAgent.isMobile()) {
            return startsWith(servicesV12Entry.getPda());
        } else {
            return startsWith(servicesV12Entry.getHref());
        }
    }

    public static Matcher<String> getSportHrefMatcher(ServicesV122Entry servicesV12Entry, UserAgent userAgent,
                                                      Language language)
    {
        String sportLinkPart = language.equals(Language.UK) ? SPORT_UK_LINK_PART : SPORT_LINK_PART;
        if (userAgent.isMobile() && userAgent.getIsTouch() == 1) {
            return startsWith(servicesV12Entry.getTouch() + sportLinkPart);
        } else if (userAgent.isMobile()) {
            return startsWith(servicesV12Entry.getPda() + sportLinkPart);
        } else {
            return startsWith(servicesV12Entry.getHref() + sportLinkPart);
        }
    }

    public static Matcher<String> getWorldHrefMatcher(ServicesV122Entry servicesV12Entry, UserAgent userAgent) {
        if (userAgent.isMobile() && userAgent.getIsTouch() == 1) {
            return startsWith(servicesV12Entry.getTouch() + WORLD_LINK_PART);
        } else if (userAgent.isMobile()) {
            return startsWith(servicesV12Entry.getPda() + WORLD_LINK_PART);
        } else {
            return startsWith(servicesV12Entry.getHref() + WORLD_LINK_PART);
        }
    }

    public static Matcher<String> getNewstabTitlekeyMatcher(String tabId) {
        return !tabId.equals(REGION) ? equalTo(tabId) : isEmptyOrNullString();
    }

    public static Matcher<String> getNewstabNameMatcher(String tabId) {
        return equalTo(NAME_MAP.get(tabId));
    }

    public static Matcher<String> getNewstabStatidMatcher(String tabId) {
        return !tabId.equals(SPORT) ? equalTo("news." + NAME_MAP.get(tabId)) : equalTo("news." + SPORT);
    }

    public static void shouldSeeNewsTab(TopnewsTab tab, String tabId) {
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getName(), getNewstabNameMatcher(tabId)));
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getKey(), equalTo(tabId)));
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getTitlekey(), getNewstabTitlekeyMatcher(tabId)));
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getStatid(), getNewstabStatidMatcher(tabId)));
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getNews(), hasSize(NEWS_NUMBER)));
    }

    public static void shouldSeeNewsSportTab(TopnewsTab tab, Region region, UserAgent userAgent) {
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getName(), getNewstabNameMatcher("sport")));
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getKey(), equalTo("sport")));
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getTitlekey(), getNewstabTitlekeyMatcher("sport")));
        if (region.getDomain().equals(Domain.KZ) && !userAgent.isMobile()) {
            shouldHaveParameter(tab, having(on(TopnewsTab.class).getStatid(), equalTo("news.theme")));
        } else {
            shouldHaveParameter(tab, having(on(TopnewsTab.class).getStatid(), getNewstabStatidMatcher("sport")));
        }
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getNews(), hasSize(NEWS_NUMBER)));
    }

    public static Matcher<String> getNewsLanguageMatcher(Region region, Language language) {
        if (region.getDomain().equals(UA) && language.equals(UK)) {
            return inLanguage(UK);
        }
        if (language.equals(TR)) {
            return inLanguage(TR);
        }
        return inLanguage(RU);
    }

    public static Matcher<String> getNewsItemHrefMatcher(ServicesV122Entry servicesV12Entry, UserAgent userAgent,
                                                         Region region) {
        if (userAgent.isMobile() && userAgent.getIsTouch() == 1) {
            return startsWith(servicesV12Entry.getTouch() + YANDSEARCH_LINK_PART);
        } else if (userAgent.isMobile()) {
            return startsWith(servicesV12Entry.getPda() + YANDSEARCH_LINK_PART);
        } else if (region.getDomain().equals(COM_TR)) {
            return startsWith("https://haber.yandex.com.tr/yandsearch");
        } else {
            return startsWith(servicesV12Entry.getHref() + YANDSEARCH_LINK_PART);
        }
    }

    public static Matcher<Iterable<String>> getNewsTabsMatcher(Region region, UserAgent userAgent) {
        if (userAgent.isMobile()) {
            return hasItems(TOUCH_TABS_REGION_MAP.get(region.getDomain()).toArray(new String[0]));
        } else {
            return hasItems(TABS_REGION_MAP.get(region.getDomain()).toArray(new String[0]));
        }
    }

    public static Matcher<String> getTopnewsHrefMatcher(Region region, ServicesV122Entry servicesV12Entry,
                                                        UserAgent userAgent) {
        if (region.getDomain().equals(COM_TR)) {
            return not(isEmptyOrNullString());
        }
        if (userAgent.isMobile() && userAgent.getIsTouch() == 1) {
            return startsWith(servicesV12Entry.getTouch());
        } else if (userAgent.isMobile()) {
            return startsWith(servicesV12Entry.getPda());
        } else {
            return startsWith(servicesV12Entry.getHref());
        }
    }
}