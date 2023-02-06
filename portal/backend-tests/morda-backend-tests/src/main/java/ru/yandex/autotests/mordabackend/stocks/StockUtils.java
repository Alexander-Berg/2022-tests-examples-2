package ru.yandex.autotests.mordabackend.stocks;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.StocksDefsEntry;
import ru.yandex.autotests.mordaexportsclient.beans.StocksEntry;
import ru.yandex.autotests.mordaexportsclient.beans.StocksFlatEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.DomainManager;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.STOCKS;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.STOCKS_DEFS;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.STOCKS_FLAT;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
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

/**
 * User: ivannik
 * Date: 25.06.2014
 */
public class StockUtils {

    public static final List<Region> STOCKS_REGIONS_MAIN = Arrays.asList(
            MOSCOW, KIEV, SANKT_PETERBURG, MINSK, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, DUBNA, ASTANA, ALMATY,
            VLADIVOSTOK, UFA, YAROSLAVL, HARKOV, DNEPROPETROVSK
    );

    public static final List<Region> STOCKS_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> STOCKS_REGIONS_ALL = new ArrayList<>();
    public static final Matcher<String> VALUE_SHORT_MATCHER = matches("\\d+(?:,\\d{2})?");
    public static final Matcher<String> VALUE_LONG_MATCHER = matches("\\d+,\\d{4}");
    public static final Matcher<String> DELTA_SHORT_MATCHER = matches("([+-−]\\d+,\\d{2}%?)|(0,00)");
    public static final Matcher<String> DELTA_LONG_MATCHER = matches("([+-−]\\d+,\\d{4})?)|(0,0000)");
    public static final List<String> STOCKS_WITHOUT_XIVA =
            Arrays.asList("1", "23", "25", "40043", "40042", "40010", "40049", "40050", "40051", "5000",
                    "5001", "5002", "10018");

    static {
        STOCKS_REGIONS_ALL.addAll(STOCKS_REGIONS_MAIN);
        STOCKS_REGIONS_ALL.addAll(STOCKS_REGIONS_TR);
    }

    public static List<StocksEntry> getStockEntries(Region region, UserAgent userAgent, String mordacontent) {
        StocksDefsEntry defaultStocks;
        if (userAgent.getIsTouch() == 1 && !region.getDomain().equals(Domain.COM_TR)) {
            defaultStocks = export(STOCKS_DEFS,
                    domain(DomainManager.getMasterDomain(region.getDomain())),
                    geo(region.getRegionIdInt()),
                    having(on(StocksDefsEntry.class).getContent(), equalTo("touch")));
        } else {
            defaultStocks = export(STOCKS_DEFS,
                    domain(region.getDomain()),
                    geo(region.getRegionIdInt()),
                    having(on(StocksDefsEntry.class).getContent(), equalTo("all")));
        }
        List<String> stockIds = Arrays.asList(defaultStocks.getStocks().split(";|,"));
        return getStockExports(stockIds);
    }

    public static List<StocksEntry> getFirefoxStockEntries(Region region) {
        StocksDefsEntry defaultStocks;
        if (region.getDomain().equals(Domain.COM_TR)) {
            defaultStocks = export(STOCKS_DEFS,
                    domain(region.getDomain()),
                    geo(region.getRegionIdInt()),
                    having(on(StocksDefsEntry.class).getContent(), equalTo("all")));
        } else {
            defaultStocks = export(STOCKS_DEFS,
                    domain(region.getDomain()),
                    geo(region.getRegionIdInt()),
                    having(on(StocksDefsEntry.class).getContent(), equalTo("firefox")));
        }

        List<String> stockIds = Arrays.asList(defaultStocks.getStocks().split(";|,"));
        return getStockExports(stockIds);
    }

    public static List<StocksEntry> getTopnewsStockEntries(StocksFlatEntry stocksFlatEntry) {
        List<String> stockIds = asList(stocksFlatEntry.getStocks().split("(,|;)"));
        return getStockExports(stockIds);
    }

    public static StocksFlatEntry getStocksFlatEntry(Region region, UserAgent userAgent) {
        return export(STOCKS_FLAT, domain(region.getDomain()), geo(region.getRegionIdInt()),
                having(on(StocksFlatEntry.class).getContent(), equalTo(getContentType(userAgent))));
    }

    private static List<StocksEntry> getStockExports(List<String> stockIds) {
        List<StocksEntry> result = new ArrayList<>();
        for (String id : stockIds) {
            result.add(export(STOCKS, having(on(StocksEntry.class).getId(), equalTo(id))));
        }
        return result;
    }

    private static String getContentType(UserAgent ua) {
        if (!ua.isMobile()) {
            return "big";
        } else if (ua.getIsTouch() == 1) {
            return "touch";
        } else {
            return "mob";
        }
    }
}
