package ru.yandex.autotests.mordabackend.geo;

import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.geo.GeoItem;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.*;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.*;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.*;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.region.Region.*;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.LYUDINOVO;

/**
 * User: ivannik
 * Date: 10.07.2014
 */
public class GeoUtils {

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);
    public static final List<Region> GEO_REGIONS_MAIN = Arrays.asList(
            SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK, ASTANA, NIZHNIY_NOVGOROD, EKATERINBURG);

    public static final List<Region> GEO_REGIONS_TR = Arrays.asList(ISTANBUL, IZMIR, BURSA, ANKARA);

    public static final List<Region> GEO_REGIONS_ALL = new ArrayList<>();
    static {
        GEO_REGIONS_ALL.addAll(GEO_REGIONS_MAIN);
        GEO_REGIONS_ALL.addAll(GEO_REGIONS_TR);
    }

    public static final DateTimeFormatter EXP_DATE_FORMAT = DateTimeFormat.forPattern("yyyy-MM-dd");
    public static final DateTimeFormatter CLENVARS_DATE_FORMAT = DateTimeFormat.forPattern("dd.MM");

    public static final String INFORMER = "informer";
    public static final String TRAFFIC = "traffic";
    public static final String METRO = "metro";
    public static final String PANORAMS = "panorams";
    public static final String ROUTES = "routes";
    public static final String TAXI = "taxi";
    public static final String POI = "poi";
    public static final String RASP = "rasp";

    public static final Map<Region, String> SPECIAL_TRAFFIC_URLS = new HashMap<Region, String>(){{
        put(ASTANA, "https://yandex.ru/maps/163/astana/probki");
    }};

    public static final Set<Region> NO_ICONS_REGIONS = new HashSet<Region>() {{
        add(LYUDINOVO);
    }};

    public static GeoServicesV14Entry getGeoService(String serviceId, Domain domain, Language language, Region region) {
        return export(SERVICES_V_14, domain(domain), lang(language), geo(region.getRegionIdInt()),
                having(on(GeoServicesV14Entry.class).getService(), equalTo(serviceId)));
    }

    public static GeoEntry getGeoEntry(String serviceId, GeoServicesV14Entry geoServiceExport, Domain domain,
                                       Language language, Region region) {
        MordaExports.MordaExport<GeoEntry> geoExport =
                selectFirst(ALL_EXPORTS, having(on(MordaExports.MordaExport.class).getName(),
                        allOf(anyOf(equalTo("geo_" + serviceId), equalTo("geo_" + serviceId + "2")),
                                not(equalTo("geo_informer")))));
        if (geoExport != null)  {
            return export(geoExport, geo(region.getRegionIdInt()), domain(domain), lang(language));
        } else if(serviceId.equals("traffic")) {
            return getTrafficEntry(geoServiceExport, region);
        } else {
            return null;
        }
    }

    private static GeoEntry getTrafficEntry(GeoServicesV14Entry geoServiceExport, Region region) {
        GeoEntry ret = new GeoEntry();
        ret.setDomain(geoServiceExport.getDomain());
        ret.setLang(geoServiceExport.getLang());
        ret.setGeo(geoServiceExport.getGeo());
        ret.setCounter(geoServiceExport.getCounter());
        if (SPECIAL_TRAFFIC_URLS.containsKey(region)) {
            ret.setUrl(SPECIAL_TRAFFIC_URLS.get(region));
        } else {
            ret.setUrl(geoServiceExport.getServiceLink());
        }
        return ret;
    }

    public static RaspEntry getRaspEntry(Region region) {
        return export(MordaExports.RASP, geo(region.getRegionIdInt()));
    }

//    public static Poi2Entry getPoiGeoEntry(String poiId) {
//        return export(POI_2, having(on(Poi2Entry.class).getId(), equalTo(poiId)));
//    }

    public static GeoInformerEntry getInformerGeoEntry(String infoText, Domain domain,
                                                       Language language, Region region, String nowYYYYMMDD) {
        return export(GEO_INFORMER, having(on(GeoInformerEntry.class).getText(), equalTo(infoText)),
                having(on(GeoInformerEntry.class).getFrom(), before(nowYYYYMMDD)),
                having(on(GeoInformerEntry.class).getTill(), anyOf(after(nowYYYYMMDD), nullValue())),
                domain(domain), lang(language), geo(region.getRegionIdInt()));
    }

    public static List<String> getExpectedIcons(Region region, Language language, Cleanvars cleanvars) {
        List<GeoServicesV14Entry> geoServicesEntries = exports(SERVICES_V_14,
                having(on(GeoServicesV14Entry.class).getServiceIcon(), equalTo(1)),
                domain(region.getDomain()), lang(language), geo(region.getRegionIdInt()));

        List<String> iconsIdsList = getOnlyExpectedIds(geoServicesEntries, region, language, cleanvars);

        int iconsCnt = iconsIdsList.size();
        if (iconsCnt <= 2) {
            return new ArrayList<>();
        } else if (iconsCnt > 2 && iconsCnt <= 5) {
            return iconsIdsList;
        } else {
            return iconsIdsList.subList(0, 5);
        }
    }

    private static List<String> getOnlyExpectedIds(List<GeoServicesV14Entry> geoServicesEntries, Region region,
                                                   Language language, Cleanvars cleanvars) {
        Collections.sort(geoServicesEntries, new Comparator<GeoServicesV14Entry>() {
            @Override
            public int compare(GeoServicesV14Entry o1, GeoServicesV14Entry o2) {
                return o2.getServiceWeight() - o1.getServiceWeight();
            }
        });
        List<GeoServicesV14Entry> toRemove = new ArrayList<>();
        for (GeoServicesV14Entry ge : geoServicesEntries) {
            if (!needed(ge, region, language, cleanvars)) {
                toRemove.add(ge);
            }
        }
        geoServicesEntries.removeAll(toRemove);
        return extract(geoServicesEntries, on(GeoServicesV14Entry.class).getService());
    }

    private static boolean needed(GeoServicesV14Entry ge, Region region, Language language, Cleanvars cleanvars) {
        switch (ge.getService()) {
            case TRAFFIC:
                return cleanvars.getTraffic().getShow() == 0 && cleanvars.getTraffic().getHref() != null;
            case POI:
                return hasItem(having(on(GeoItem.class).getService(), equalTo(POI))).matches(cleanvars.getGeo().getListIcon());
            case METRO:
            case PANORAMS:
            case ROUTES:
            case TAXI:
                return getGeoEntry(ge.getService(), getGeoService(ge.getService(), region.getDomain(), language, region),
                        region.getDomain(), language, region) != null;
            case RASP:
                return getRaspEntry(region) != null;
            case INFORMER:
                return export(GEO_INFORMER, having(on(GeoInformerEntry.class).getTill(), after(cleanvars.getYYYYMMDD())),
                        having(on(GeoInformerEntry.class).getFrom(), before(cleanvars.getYYYYMMDD())),
                        domain(region.getDomain()), lang(language), geo(region.getRegionIdInt())) != null;
            default:
                return false;
        }
    }

    public static List<String> getExpectedLinks(Region region, Language language, Cleanvars cleanvars) {

        List<GeoServicesV14Entry> geoServicesEntries = exports(SERVICES_V_14,
                having(on(GeoServicesV14Entry.class).getServiceIcon(), equalTo(1)),
                domain(region.getDomain()), lang(language), geo(region.getRegionIdInt()));

        List<String> linksIdsList = getOnlyExpectedIds(geoServicesEntries, region, language, cleanvars);

        List<String> notIcon = getOnlyExpectedIds(exports(SERVICES_V_14,
                        having(on(GeoServicesV14Entry.class).getServiceIcon(), equalTo(0)),
                        domain(region.getDomain()), lang(language), geo(region.getRegionIdInt())),
                region, language, cleanvars);

        int iconsCnt = linksIdsList.size();
        if (iconsCnt <= 2) {
            linksIdsList.addAll(notIcon);
            return linksIdsList;
        } else if (iconsCnt > 2 && iconsCnt <= 5) {
            return notIcon;
        } else {
            linksIdsList = linksIdsList.subList(5, iconsCnt);
            linksIdsList.addAll(notIcon);
            return linksIdsList;
        }
    }
}
