package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.CoreMatchers;
import org.hamcrest.Matcher;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.utils.CityGeoInfo;
import ru.yandex.autotests.mainmorda.utils.GeoIconType;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mainmorda.utils.CityGeoInfo.GeoIconInfo;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.METRO_HRK;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.METRO_KIEV;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.METRO_MSK;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.METRO_SPB;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.PANORAMS;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.RASP;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.ROUTES;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.TAXI;
import static ru.yandex.autotests.mainmorda.utils.GeoIconType.TRAFFIC;
import static ru.yandex.autotests.mainmorda.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.GEO_METRO_2;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.GEO_PANORAMS;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.GEO_ROUTES;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.GEO_SERVICES;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.GEO_TAXI;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoServicesEntryMatcher.with;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.GeoLinks.GEO_LINK_RASP;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.POI_SEARCH_ATM;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.POI_SEARCH_BANK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.POI_SEARCH_CAFE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.POI_SEARCH_DRUGSTORE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.POI_SEARCH_GASOLINE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.POI_SEARCH_MOVIE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.LYUDINOVO;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: alex89
 * Date: 04.05.12
 */
public class GeoIconsData {
    private static final Properties CONFIG = new Properties();

    private static Matcher<String> getPanoramUrl(Region region, Domain d) {
        return startsWith(normalizeUrl(
                export(GEO_PANORAMS, geo(region.getRegionIdInt()), domain(d), lang(CONFIG.getLang())).getUrl(),
                CONFIG.getProtocol()));
    }

    private static Matcher<String> getTaxiUrl(Region region, Domain d) {
        return startsWith(normalizeUrl(
                export(GEO_TAXI, domain(d), lang(CONFIG.getLang()), geo(region.getRegionIdInt())).getUrl(),
                CONFIG.getProtocol()));
    }

    private static Matcher<String> getMetroUrl(Region region, Domain d) {
        return startsWith(normalizeUrl(
                export(GEO_METRO_2, domain(d), lang(CONFIG.getLang()), geo(region.getRegionIdInt())).getUrl(),
                CONFIG.getProtocol()));
    }

    private static Matcher<String> getRoutesUrl(Region region, Domain d) {
        return startsWith(normalizeUrl(
                export(GEO_ROUTES, domain(d), lang(CONFIG.getLang()), geo(region.getRegionIdInt())).getUrl(),
                CONFIG.getProtocol()));
    }

    private static Matcher<String> getTrafficUrl(Region region, Domain d) {
        return startsWith(
                normalizeUrl(export(GEO_SERVICES, domain(d), lang(CONFIG.getLang()), geo(region.getRegionIdInt()),
                        with().service("traffic")).getServiceLink(),
                        CONFIG.getProtocol()));
    }

    private static Matcher<String> getRaspUrl(Region region, Domain d) {
        return startsWith(
                normalizeUrl(export(GEO_SERVICES, domain(d), lang(CONFIG.getLang()), geo(region.getRegionIdInt()),
                        with().service("rasp")).getServiceLink(),
                        CONFIG.getProtocol()));
    }

    public static final CityGeoInfo SPB_INFO = new CityGeoInfo(
            SANKT_PETERBURG,
            Arrays.asList(
                    new GeoIconInfo(METRO_SPB, getMetroUrl(SANKT_PETERBURG, RU),
                            CoreMatchers.equalTo("http://metro.yandex.ru/spb")),
                    new GeoIconInfo(TAXI, getTaxiUrl(SANKT_PETERBURG, RU),
                            startsWith("https://taxi.yandex.ru/?from=mtaxi_geoblock_spb")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(SANKT_PETERBURG, RU),
                            startsWith("http://maps.yandex.ru/" +
                                    "?text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%A1%D0%B0%D0%BD%D0%BA%D1%82")),
                    new GeoIconInfo(ROUTES, getRoutesUrl(SANKT_PETERBURG, RU),
                            startsWith("http://maps.yandex.ru/?rtext=&sll=30.313497%2C59.938531")),
                    new GeoIconInfo(RASP, getRaspUrl(SANKT_PETERBURG, RU),
                            startsWith("http://rasp.yandex.ru/"))
            ),
            Arrays.asList(
                    new LinkInfo(CoreMatchers.equalTo(getTranslation(GEO_LINK_RASP, CONFIG.getLang())),
                            getRaspUrl(SANKT_PETERBURG, RU)
                    )
            )
    );

    public static final CityGeoInfo MSK_INFO = new CityGeoInfo(
            MOSCOW,
            Arrays.asList(
                    new GeoIconInfo(METRO_MSK, getMetroUrl(MOSCOW, RU),
                            CoreMatchers.equalTo("http://metro.yandex.ru/moscow")),
                    new GeoIconInfo(TAXI, getTaxiUrl(MOSCOW, RU),
                            startsWith("https://taxi.yandex.ru/?from=mtaxi_geoblock_msk")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(MOSCOW, RU),
                            startsWith("http://maps.yandex.ru/?index=&ll=37.621029%2C55.753954")),
                    new GeoIconInfo(ROUTES, getRoutesUrl(MOSCOW, RU),
                            startsWith("http://maps.yandex.ru/?rtext=&sll=37.617671%2C55.755768")),
                    new GeoIconInfo(RASP, getRaspUrl(MOSCOW, RU),
                            startsWith("http://rasp.yandex.ru/"))
            ),
            Arrays.asList(
                    new LinkInfo(CoreMatchers.equalTo(getTranslation(GEO_LINK_RASP, CONFIG.getLang())),
                            getRaspUrl(MOSCOW, RU)
                    )
            )
    );

    public static final CityGeoInfo KIEV_INFO = new CityGeoInfo(
            KIEV,
            Arrays.asList(
                    new GeoIconInfo(METRO_KIEV, getMetroUrl(KIEV, UA),
                            CoreMatchers.equalTo("http://metro.yandex.ru/kiev")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(KIEV, UA),
                            startsWith("http://maps.yandex.ua/?ll=30.513522%2C50.448554")),
                    new GeoIconInfo(ROUTES, getRoutesUrl(KIEV, UA),
                            startsWith("http://maps.yandex.ua/?rtext=&sll=30.522301%2C50.451118")),
                    new GeoIconInfo(RASP, getRaspUrl(KIEV, UA),
                            startsWith("http://rasp.yandex.ua/"))
            ),
            Collections.<LinkInfo>emptyList()
    );

    public static final CityGeoInfo HARKOV_INFO = new CityGeoInfo(
            HARKOV,
            Arrays.asList(
                    new GeoIconInfo(METRO_HRK, getMetroUrl(HARKOV, UA),
                            CoreMatchers.equalTo("http://metro.yandex.ru/kharkov")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(HARKOV, UA),
                            startsWith("http://maps.yandex.ua/?index=&ll=36.233932%2C49.998886")),
                    new GeoIconInfo(ROUTES, getRoutesUrl(HARKOV, UA),
                            startsWith("http://maps.yandex.ua/?rtext=&sll=36.279065%2C49.980149")),
                    new GeoIconInfo(RASP, getRaspUrl(HARKOV, UA),
                            startsWith("http://rasp.yandex.ua/"))
            ),
            new ArrayList<LinkInfo>()
    );

    public static final CityGeoInfo MINSK_INFO = new CityGeoInfo(
            MINSK,
            Arrays.asList(
                    new GeoIconInfo(ROUTES, getRoutesUrl(MINSK, BY),
                            startsWith("http://maps.yandex.ru/?rtext=&sll=27.558759%2C53.901090")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(MINSK, BY),
                            startsWith("http://maps.yandex.ru/?ll=27.559225%2C53.900585")),
                    new GeoIconInfo(RASP, getRaspUrl(MINSK, BY),
                            CoreMatchers.startsWith("http://rasp.yandex.by/"))
            ),
            Collections.<LinkInfo>emptyList()
    );

    public static final CityGeoInfo ASTANA_INFO = new CityGeoInfo(
            ASTANA,
            Arrays.asList(
                    new GeoIconInfo(TRAFFIC, CoreMatchers.equalTo("http://maps.yandex.ru/astana_traffic"),
                            startsWith("http://maps.yandex.ru/?ll=71.480124%2C51.151817")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(ASTANA, KZ),
                            startsWith("http://maps.yandex.ru/?ll=71.431187%2C51.154073")),
                    new GeoIconInfo(ROUTES, getRoutesUrl(ASTANA, KZ),
                            startsWith("http://maps.yandex.ru/?rtext=&sll=71.480124%2C51.151817")),
                    new GeoIconInfo(RASP, getRaspUrl(ASTANA, KZ),
                            CoreMatchers.equalTo("http://rasp.yandex.kz/"))
            ),
            new ArrayList<LinkInfo>()
    );

    public static final CityGeoInfo NNOVGOROD_INFO = new CityGeoInfo(
            NIZHNIY_NOVGOROD,
            Arrays.asList(
                    new GeoIconInfo(TAXI, getTaxiUrl(NIZHNIY_NOVGOROD, RU),
                            CoreMatchers.equalTo("https://taxi.yandex.ru/?from=mtaxi_geoblock_nno")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(NIZHNIY_NOVGOROD, RU),
                            CoreMatchers.equalTo("http://maps.yandex.ru/?index=&ll=43.995938%2C56.329922")),
                    new GeoIconInfo(ROUTES, getRoutesUrl(NIZHNIY_NOVGOROD, RU),
                            startsWith("http://maps.yandex.ru/?rtext=&sll=44.001486%2C56.324142")),
                    new GeoIconInfo(RASP, getRaspUrl(NIZHNIY_NOVGOROD, RU),
                            CoreMatchers.equalTo("http://rasp.yandex.ru/"))
            ),
            new ArrayList<LinkInfo>()
    );

    public static final CityGeoInfo EKATERINBURG_INFO = new CityGeoInfo(
            EKATERINBURG,
            Arrays.asList(
                    new GeoIconInfo(TAXI, getTaxiUrl(EKATERINBURG, RU),
                            startsWith("https://taxi.yandex.ru/?from=mtaxi_geoblock_ekb")),
                    new GeoIconInfo(PANORAMS, getPanoramUrl(EKATERINBURG, RU),
                            startsWith("http://maps.yandex.ru/?index=&ll=60.604131%2C56.838288")),
                    new GeoIconInfo(ROUTES,getRoutesUrl(EKATERINBURG, RU),
                            startsWith("http://maps.yandex.ru/?rtext=&sll=60.597223%2C56.837992")),
                    new GeoIconInfo(RASP, getRaspUrl(EKATERINBURG, RU),
                            CoreMatchers.equalTo("http://rasp.yandex.ru/"))

            ),
            new ArrayList<LinkInfo>()
    );

    public static final CityGeoInfo LYUDINOVO_INFO = new CityGeoInfo(
            LYUDINOVO,
            new ArrayList<GeoIconInfo>(),
            Arrays.asList(
                    new LinkInfo(matches(".*[Пп]ан[оа]рам.*"),
                            equalTo("https://maps.yandex.ru/?index=&ll=43.506343%2C55.219296" +
                                    "&spn=3.515625%2C4.913219&z=6&l=map%2Csta%2Cstv"),
                                    hasAttribute(HREF, startsWith("https://maps.yandex.ru/"))
                            ),
                    new LinkInfo(CoreMatchers.equalTo(getTranslation(GEO_LINK_RASP, CONFIG.getLang())),
                            getRaspUrl(LYUDINOVO, RU)
                    )
            )
    );

    public static final List<CityGeoInfo> CITY_OBJECTS_LIST = Arrays.asList(
            SPB_INFO, MSK_INFO, KIEV_INFO, HARKOV_INFO, ASTANA_INFO, MINSK_INFO, NNOVGOROD_INFO, EKATERINBURG_INFO,
            LYUDINOVO_INFO
    );

    public static final List<CityGeoInfo> CITY_ADAPTIVE_TEST_LIST = Arrays.asList(
            SPB_INFO, MSK_INFO
    );

    public static final Dimension DEFAULT_SIZE = new Dimension(1500, 600);
    public static final Dimension SMALL_SIZE = new Dimension(500, 600);

    private static final Language LANG_POI;

    static {
        if (CONFIG.getLang().equals(Language.UK) || CONFIG.getLang().equals(Language.BE)) {
            LANG_POI = CONFIG.getLang();
        } else {
            LANG_POI = Language.RU;
        }
    }


    public static final String ATM_URL_PATTERN =
            UrlManager.encodeRequest("rubric:" + getTranslation(POI_SEARCH_ATM, LANG_POI));
    public static final String CAFE_URL_PATTERN =
            UrlManager.encodeRequest("rubric:" + getTranslation(POI_SEARCH_CAFE, LANG_POI));
    public static final String DRUGS_URL_PATTERN =
            UrlManager.encodeRequest("rubric:" + getTranslation(POI_SEARCH_DRUGSTORE, LANG_POI));
    public static final String BANK_URL_PATTERN =
            UrlManager.encodeRequest("rubric:" + getTranslation(POI_SEARCH_BANK, LANG_POI));
    public static final String MOVIE_URL_PATTERN =
            UrlManager.encodeRequest("rubric:" + getTranslation(POI_SEARCH_MOVIE, LANG_POI));
    public static final String GAS_URL_PATTERN =
            UrlManager.encodeRequest("rubric:" + getTranslation(POI_SEARCH_GASOLINE, LANG_POI));

    public enum GeoRandomIcons {
        ATM(GeoIconType.ATM, ATM_URL_PATTERN),
        CAFE(GeoIconType.CAFE, CAFE_URL_PATTERN),
        DRUGS(GeoIconType.DRUGSTORE, DRUGS_URL_PATTERN),
        BANK(GeoIconType.BANK, BANK_URL_PATTERN),
        MOVIE(GeoIconType.MOVIE, MOVIE_URL_PATTERN),
        GAS(GeoIconType.GAZ, GAS_URL_PATTERN);

        private final GeoIconType type;
        private final String urlPattern;

        private GeoRandomIcons(GeoIconType type, String urlPattern) {
            this.type = type;
            this.urlPattern = urlPattern;
        }

        public String getUrlPattern(WebDriver driver) {
            if (Domain.getDomain(driver.getCurrentUrl()).equals(Domain.UA)) {
                return "http://maps.yandex.ua/?text=" + urlPattern;
            } else {
                return "http://maps.yandex.ru/?text=" + urlPattern;
            }
        }

        public static GeoRandomIcons getIcon(String type) {
            for (GeoRandomIcons icon : GeoRandomIcons.values()) {
                if (type.contains(icon.type.toString())) {
                    return icon;
                }
            }
            return null;
        }
    }
}