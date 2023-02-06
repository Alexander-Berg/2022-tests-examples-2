package ru.yandex.autotests.mordabackend.weather;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.LinkUtils;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordaexportsclient.beans.WeatherMappingEntry;
import ru.yandex.autotests.mordaexportslib.ExportProvider;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.geobase.beans.GeobaseRegionData;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.lang.String.format;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.AFTERNOON;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.EVENING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.MORNING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.NIGHT;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ADANA;
import static ru.yandex.autotests.utils.morda.region.Region.ALANYA;
import static ru.yandex.autotests.utils.morda.region.Region.ALMATY;
import static ru.yandex.autotests.utils.morda.region.Region.ANTALYA;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.BURSA;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.CHLYA;
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
import static ru.yandex.autotests.utils.morda.region.Region.VOROJBA;
import static ru.yandex.autotests.utils.morda.region.Region.YAROSLAVL;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10.07.14
 */
public class WeatherUtils {
    public static final List<Region> WEATHER_REGIONS_MAIN = Arrays.asList(
            MOSCOW, KIEV, SANKT_PETERBURG, MINSK, EKATERINBURG, PERM,
            SAMARA, CHELYABINSK, NOVOSIBIRSK, DUBNA, ASTANA, ALMATY,
            VLADIVOSTOK, UFA, YAROSLAVL, HARKOV, DNEPROPETROVSK,
            VOROJBA, CHLYA
    );


    public static final List<Region> WEATHER_REGIONS_TR = Arrays.asList(
            ISTANBUL, BURSA, ALANYA, ANTALYA, IZMIR, ADANA, GAZIANTEP, MERSIN
    );

    public static final List<Region> WEATHER_REGIONS_ALL = new ArrayList<>();
    public static final Map<Integer, Integer> WEATHER_REMAP;
    public static final Matcher<String> TEMPERATURE_MATCHER = matches("0|([+−-]?[1-9]\\d?)");
    private static final Map<Integer, TextID> DAY_TIME_MAP = new HashMap<Integer, TextID>() {{
        put(0, MORNING);
        put(1, AFTERNOON);
        put(2, EVENING);
        put(3, NIGHT);
    }};

    static {
        WEATHER_REGIONS_ALL.addAll(WEATHER_REGIONS_TR);
        WEATHER_REGIONS_ALL.addAll(WEATHER_REGIONS_MAIN);
    }

    static {
        WEATHER_REMAP = new HashMap<>();
        for (WeatherMappingEntry entry : ExportProvider.exports(MordaExports.WEATHER_MAPPING, notNullValue())) {
            WEATHER_REMAP.put(entry.getGeo(), entry.getShowGeo());
        }
    }

    public static Matcher<String> getT2NameMatcher(int hour, Language language) {
        return equalTo(getTranslation(DAY_TIME_MAP.get(hour / 6), language));
    }

    public static Matcher<String> getT3NameMatcher(int hour, Language language) {
        return equalTo(getTranslation(DAY_TIME_MAP.get(((hour + 6) % 24) / 6), language));
    }

    public static String urlWithMasterDomain(String url) {
        return url.replaceAll("\\.(ua|by|kz)(?=(/|$))", Domain.RU.toString());
    }

    public static Matcher<String> getMobUrlMatcher(ServicesV122Entry servicesV12Entry,
                                                   Region region, UserAgent userAgent) {
        String baseUrl;
        if ((userAgent.isMobile() && userAgent.getIsTouch() != 1) || region.getDomain().equals(Domain.COM_TR)) {
            baseUrl = servicesV12Entry.getPda();
        } else {
            baseUrl = servicesV12Entry.getHref();
        }
        baseUrl = LinkUtils.normalizeUrl(baseUrl);
        int id = getWeatherGeoId(region);
        GeobaseRegionData regionT = new GeobaseRegion(region.getRegionIdInt()).getData();

        return urlMatcher(baseUrl)
                .path(anyOf(
                        containsString(String.valueOf(regionT.getId())),
                        containsString(regionT.getEnName().toLowerCase().replaceAll(" ", "-"))
                ))
                .build();
    }

    public static int getWeatherGeoId(Region region) {
        if (WEATHER_REMAP.containsKey(region.getRegionIdInt())) {
            return WEATHER_REMAP.get(region.getRegionIdInt());
        }
        return region.getRegionIdInt();
    }

    public static Matcher<String> getUrlMatcher(ServicesV122Entry servicesV12Entry, Region region, UserAgent userAgent) {
        int id = getWeatherGeoId(region);
        GeobaseRegionData regionT = new GeobaseRegion(region.getRegionIdInt()).getData();
        String url;
        if (userAgent.isMobile()) {
            url = servicesV12Entry.getPda();
        } else {
            url = servicesV12Entry.getHref();
        }
        return urlMatcher(url)
                .path(containsString(regionT.getEnName().toLowerCase().replaceAll(" ", "-")))
                .build();

    }

    public static Matcher<String> getHrefMatcher(ServicesV122Entry servicesV12Entry,
                                                 Region region, UserAgent userAgent) {
        int id = getWeatherGeoId(region);
        GeobaseRegionData regionT = new GeobaseRegion(region.getRegionIdInt()).getData();
        String url;
        if (userAgent.isMobile()) {
            url = servicesV12Entry.getPda();
        } else {
            url = servicesV12Entry.getHref();
        }
        return urlMatcher(url)
                .path(
                        containsString(regionT.getEnName().toLowerCase().replaceAll(" ", "-"))
                ).build();

    }

    public static Matcher<String> getNoticeHrefMatcher(ServicesV122Entry servicesV12Entry,
                                                       Region region, UserAgent userAgent) {
        int id = getWeatherGeoId(region);
        GeobaseRegionData regionT = new GeobaseRegion(region.getRegionIdInt()).getData();
        String url;
        if (userAgent.isMobile()) {
            url = servicesV12Entry.getPda();
        } else {
            url = servicesV12Entry.getHref();
        }

        return urlMatcher(url)
                .path(allOf(
                        containsString(regionT.getEnName().toLowerCase().replaceAll(" ", "-")),
                        containsString("/details")
                        )
                )
                .build();
    }

    public static Matcher<String> getFirefoxUrlMatcher(ServicesV122Entry servicesV12Entry,
                                                   Region region, UserAgent userAgent) {

        GeobaseRegionData regionT = new GeobaseRegion(region.getRegionIdInt()).getData();
        String baseUrl;
        if (COM_TR.equals(region.getDomain())){
            baseUrl = servicesV12Entry.getHref();
        } else {
            baseUrl = format("https://yandex.%s/pogoda/", servicesV12Entry.getDomain());
        }

        return urlMatcher(baseUrl)
                .path(
                        containsString(regionT.getEnName().toLowerCase().replaceAll(" ", "-"))
                )
                .build();
    }


}
