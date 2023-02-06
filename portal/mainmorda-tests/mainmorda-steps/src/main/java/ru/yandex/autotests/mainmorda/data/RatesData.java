package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordaexportsclient.beans.StocksDefsEntry;
import ru.yandex.autotests.mordaexportsclient.beans.TopnewsStocksEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.text.SimpleDateFormat;
import java.util.*;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.STOCKS_DEFS;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.TOPNEWS_STOCKS;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.TODAY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.TOMORROW;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Rates.BUYING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Rates.SELLING;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: leonsabr
 * Date: 02.04.12
 */
public class RatesData {
    private static final Properties CONFIG = new Properties();

    private static final String HOME = "home";
    private static final String RATES = "rates";
    private static final String STOCKS = "stocks.";
    private static final String TEXT = ".text";
    private static final String SHORT = ".short";

    private static final SimpleDateFormat SDF = new SimpleDateFormat("dd/MM");
    private static final Calendar MSK_CALENDAR = Calendar.getInstance();
    private static final Calendar CALENDAR = Calendar.getInstance(CONFIG.getBaseDomain().getCapital().getTimezone());
    private static final int DAY = CALENDAR.get(Calendar.DAY_OF_WEEK);

    private static final boolean IS_WEEKEND = DAY == Calendar.SATURDAY || DAY == Calendar.SUNDAY;
    private static final boolean IS_AFTER_SIXTEEN =
            MSK_CALENDAR.get(Calendar.HOUR_OF_DAY) >= 16 && CALENDAR.get(Calendar.HOUR_OF_DAY) >= 12;
    private static final boolean IS_AFTER_TWELVE =
            MSK_CALENDAR.get(Calendar.HOUR_OF_DAY) >= 12 && CALENDAR.get(Calendar.HOUR_OF_DAY) >= 12;


    private static final Matcher<String> TODAY_SELL_TEXT_RU;

    static {
        if (IS_WEEKEND) {
            CALENDAR.add(Calendar.DAY_OF_MONTH, -DAY);
            TODAY_SELL_TEXT_RU = equalTo(SDF.format(CALENDAR.getTime()));
        } else {
            TODAY_SELL_TEXT_RU = equalTo(getTranslation(TODAY, CONFIG.getLang()));
        }
    }

    private static final Matcher<String> TOMORROW_BUY_TEXT_RU;

    static {
        if (IS_WEEKEND) {
            TOMORROW_BUY_TEXT_RU = equalTo("");
        } else if (IS_AFTER_TWELVE) {
            TOMORROW_BUY_TEXT_RU = equalTo(getTranslation(TOMORROW, CONFIG.getLang()));
        } else {
            TOMORROW_BUY_TEXT_RU = equalTo("");
        }
    }

    private static final Matcher<String> TODAY_SELL_TEXT_KZ;

    static {
        if (DAY == Calendar.SATURDAY) {
            CALENDAR.add(Calendar.DAY_OF_MONTH, -1);
            TODAY_SELL_TEXT_KZ = equalTo(SDF.format(CALENDAR.getTime()));
        } else if (DAY == Calendar.SUNDAY) {
            CALENDAR.add(Calendar.DAY_OF_MONTH, -2);
            TODAY_SELL_TEXT_KZ = equalTo(SDF.format(CALENDAR.getTime()));
        } else {
            TODAY_SELL_TEXT_KZ = equalTo(getTranslation(TODAY, CONFIG.getLang()));
        }
    }

    private static String getTomorrow() {
        String tomorrow;
        if (DAY == Calendar.FRIDAY) {
            CALENDAR.add(Calendar.DAY_OF_MONTH, 3);
            tomorrow = SDF.format(CALENDAR.getTime());
        } else if (DAY == Calendar.SATURDAY) {
            CALENDAR.add(Calendar.DAY_OF_MONTH, 2);
            tomorrow = SDF.format(CALENDAR.getTime());
        } else {
            tomorrow = getTranslation(TOMORROW, CONFIG.getLang());
        }
        return tomorrow;
    }

    private static final Matcher<String> TOMORROW_BUY_TEXT_KZ;

    static {

        if (IS_WEEKEND || IS_AFTER_SIXTEEN) {
            TOMORROW_BUY_TEXT_KZ = equalTo(getTomorrow());
        } else {
            TOMORROW_BUY_TEXT_KZ = equalTo("");
        }
    }

    private static final Matcher<String> TODAY_SELL_TEXT_UA_BY;
    private static final Matcher<String> TOMORROW_BUY_TEXT_UA_BY;

    static {
        TODAY_SELL_TEXT_UA_BY = equalTo(getTranslation(BUYING, CONFIG.getLang()));
        TOMORROW_BUY_TEXT_UA_BY = equalTo(getTranslation(SELLING, CONFIG.getLang()));
    }

    private static final Map<Domain, Matcher<String>> TODAY_SELL_MAP = new HashMap<Domain, Matcher<String>>() {{
        put(Domain.RU, TODAY_SELL_TEXT_RU);
        put(Domain.KZ, TODAY_SELL_TEXT_KZ);
        put(Domain.BY, TODAY_SELL_TEXT_UA_BY);
        put(Domain.UA, TODAY_SELL_TEXT_UA_BY);
    }};

    private static final Map<Domain, Matcher<String>> TOMORROW_BUY_MAP = new HashMap<Domain, Matcher<String>>() {{
        put(Domain.RU, TOMORROW_BUY_TEXT_RU);
        put(Domain.KZ, TOMORROW_BUY_TEXT_KZ);
        put(Domain.BY, TOMORROW_BUY_TEXT_UA_BY);
        put(Domain.UA, TOMORROW_BUY_TEXT_UA_BY);
    }};

    public static final Matcher<String> TODAY_SELL_TEXT = TODAY_SELL_MAP.get(CONFIG.getBaseDomain());
    public static final Matcher<String> TOMORROW_BUY_TEXT = TOMORROW_BUY_MAP.get(CONFIG.getBaseDomain());

    private static final List<String> RU_SET = Arrays.asList("2000", "2002", "1006");
    private static final List<String> UA_SET = Arrays.asList("40043", "40042");
    private static final List<String> BY_SET = Arrays.asList("40049", "40050", "40051");
    private static final List<String> KZ_SET = Arrays.asList("5000", "5001", "5002");

    private static final Map<Domain, List<String>> REGIONAL_RATES = new HashMap<Domain, List<String>>() {{
        put(Domain.RU, RU_SET);
        put(Domain.UA, UA_SET);
        put(Domain.KZ, KZ_SET);
        put(Domain.BY, BY_SET);
    }};

    public static final List<String> DEFAULT_INLINE_RATES;
    static {
        TopnewsStocksEntry entry = export(TOPNEWS_STOCKS, domain(CONFIG.getBaseDomain()),
                geo(CONFIG.getBaseDomain().getCapital().getRegionIdInt()),
                having(on(TopnewsStocksEntry.class).getContent(), equalTo("big")));
        if (entry != null) {
            DEFAULT_INLINE_RATES = Arrays.asList(entry.getStocks().split("(;|,)"));
        } else {
            DEFAULT_INLINE_RATES = Collections.emptyList();
        }
    }

    public static final List<String> DEFAULT_RATES = Arrays.asList(export(STOCKS_DEFS, domain(CONFIG.getBaseDomain()),
            geo(CONFIG.getBaseDomain().getCapital().getRegionIdInt()),
            having(on(StocksDefsEntry.class).getContent(), equalTo("all"))).getStocks().split(";"));

    public static String getStocksId(String href) {
        return href.substring(href.lastIndexOf("/") + 1, href.lastIndexOf("."));
    }

    public static String getText(String stocksId, boolean isShort) {
        return getTranslation(HOME, RATES, STOCKS + stocksId + (isShort ? SHORT : TEXT), CONFIG.getLang());
    }

    private static final Map<Domain, Integer> TEST_SIZE_MAP = new HashMap<Domain, Integer>() {{
        put(Domain.RU, 58);
        put(Domain.KZ, 34);
        put(Domain.BY, 37);
        put(Domain.UA, 41);
    }};


    public static final int TEST_SIZE = TEST_SIZE_MAP.get(CONFIG.getBaseDomain());

    public static final Matcher<String> RATE_MATCHER = matches("([0-9]+),[0-9]{4}");
    public static final Matcher<String> RATE_DIFF_MATCHER = matches("(([−]|[+])[0-9]+,[0-9]+)|(0,00)");

    public static boolean isInline(Region region) {
        return !exports(TOPNEWS_STOCKS, domain(CONFIG.getBaseDomain()), geo(region.getRegionIdInt()),
                having(on(TopnewsStocksEntry.class).getContent(), equalTo("big"))).isEmpty();
    }
}
