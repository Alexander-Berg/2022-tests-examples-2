package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.utils.LinkHrefInfo;
import ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.data.MordaDate;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.region.RegionManager;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.isEmptyString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.News.SWITCH_BLOGS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.News.SWITCH_IN_WORLD;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.News.SWITCH_NEWS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.News.SWITCH_SPORT;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;

/**
 * User: alex89
 * Date: 17.04.12
 */
public class NewsBlockData {
    private static final Properties CONFIG = new Properties();

    public static final String TIME_PAGE_URL_PATTERN = "https://time.yandex%s";
    public static final String NEWS_URL_PATTERN = "http://news.yandex%s/";
    public static final String NEWS_HTTPS_URL_PATTERN = "https://news.yandex%s/";

    private static final String BLOGS_URL_RU = "http://blogs.yandex.ru/";
    private static final String BLOGS_URL_BY = "http://blogs.yandex.by/";
    private static final String BLOGS_URL_UA = "http://blogs.yandex.ua/";
    private static final String SPORT_URL = "http://news.yandex.kz/sport.html";

    public static final Map<Domain, String> BLOGS_SPORT_URL = new HashMap<Domain, String>() {{
        put(Domain.RU, BLOGS_URL_RU);
        put(Domain.BY, BLOGS_URL_BY);
        put(Domain.UA, BLOGS_URL_UA);
        put(KZ, SPORT_URL);
    }};

    public static final Matcher<String> BLOGS_URL = startsWith(BLOGS_SPORT_URL.get(CONFIG.getBaseDomain()));
    public static final Matcher<String> BLOGS_ITEM_URL;

    static {
        if (CONFIG.domainIs(KZ)) {
            BLOGS_ITEM_URL = startsWith("http://news.yandex.kz/yandsearch?cl4url=");
        } else {
            BLOGS_ITEM_URL = startsWith(BLOGS_SPORT_URL.get(CONFIG.getBaseDomain()));
        }
    }

    public static final Matcher<String> NEWS_URL = startsWith(String.format(NEWS_URL_PATTERN, CONFIG.getBaseDomain()));
    public static final Matcher<String> NEWS_HTTPS_URL = startsWith(String.format(NEWS_HTTPS_URL_PATTERN, CONFIG.getBaseDomain()));
    public static final Matcher<String> TIME_URL =
            startsWith(String.format(NewsBlockData.TIME_PAGE_URL_PATTERN, CONFIG.getBaseDomain()));

    public static final LinkHrefInfo TIME_HREF = new LinkHrefInfo(not(isEmptyString()), TIME_URL);
    public static final LinkInfo NEWS_LINK = new LinkInfo(not(isEmptyString()), NEWS_HTTPS_URL);
    public static final LinkInfo SPORT_LINK = new LinkInfo(not(isEmptyString()), BLOGS_ITEM_URL);

    public static final Matcher<String> NEWS_TEXT = equalTo(getTranslation(SWITCH_NEWS, CONFIG.getLang()));
    public static final Matcher<String> REGION_NEWS_TEXT;

    static {
        if (CONFIG.domainIs(KZ)) {
            REGION_NEWS_TEXT = equalTo(getTranslation(SWITCH_IN_WORLD, CONFIG.getLang()));
        } else {
            REGION_NEWS_TEXT = equalTo(getTranslation("regions", "news",
                    CONFIG.getBaseDomain().getCapital().toString(),
                    CONFIG.getLang()));
        }
    }

    public static final Matcher<String> SPORT_TEXT;

    static {
        if (CONFIG.domainIs(KZ)) {
            SPORT_TEXT = equalTo(getTranslation(SWITCH_SPORT, CONFIG.getLang()));
        } else {
            SPORT_TEXT = equalTo(getTranslation(SWITCH_BLOGS, CONFIG.getLang()));
        }
    }


    public static final Matcher<String> HOUR_MATCHER = matches("[0-1][0-9]|2[0-3]");
    public static final Matcher<String> MINUTE_MATCHER = matches("[0-5][0-9]");
    public static final Matcher<String> DIVIDER_MATCHER = anyOf(equalTo(":"), equalTo(""));
    public static final int DEFAULT_NEWS_SIZE = 5;

    public static Matcher<String> getWDayMatcher(Region region) {
        int day = RegionManager.getDayOfWeek(region);
        return anyOf(equalTo(getTranslation(MordaDate.DAY_OF_WEEK.get(day), CONFIG.getLang())),
                equalTo(getTranslation(MordaDate.SHORTDAY_OF_WEEK.get(day), CONFIG.getLang())));
    }

    public static Matcher<String> getDayMatcher(Region region) {
        int day = RegionManager.getDayOfMonth(region);
        return Matchers.equalTo(Integer.toString(day));
    }

    public static Matcher<String> getMonthMatcher(Region region) {
        int month = RegionManager.getMonth(region);
        return Matchers.equalTo(getTranslation(MordaDate.MONTH_NAME.get(month), CONFIG.getLang()) + ",");
    }

    private static final Map<Domain, Language> DOMAIN_TO_LANGUAGE = new HashMap<Domain, Language>() {{
        put(Domain.RU, Language.RU);
        put(Domain.UA, Language.UK);
        put(Domain.BY, Language.BE);
        put(KZ, Language.KK);
    }};

    public static final Language NEWS_LANGUAGE = DOMAIN_TO_LANGUAGE.get(CONFIG.getBaseDomain());
}