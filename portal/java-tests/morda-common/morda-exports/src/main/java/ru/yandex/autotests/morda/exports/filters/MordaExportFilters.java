package ru.yandex.autotests.morda.exports.filters;

import org.jetbrains.annotations.NotNull;
import org.joda.time.LocalDateTime;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithContent;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithDomain;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithFrom;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithGeo;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithId;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithLang;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithMordatype;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithPlatform;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithTill;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithWeekDay;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

import static java.util.Arrays.asList;
/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/08/15
 */
public class MordaExportFilters {

    public static final Map<String, List<String>> DOMAIN_IN_DOMAIN_MAP = new HashMap<String, List<String>>() {{
        put("ru", asList("all", "ru", "kubr-ua", "all-com.tr"));
        put("ua", asList("all", "ua", "kub", "all-com.tr"));
        put("by", asList("all", "by", "kub", "kubr-ua", "all-com.tr"));
        put("kz", asList("all", "kz", "kub", "kubr-ua", "all-com.tr"));
        put("com", asList("all", "com", "all-com.tr"));
        put("com.tr", asList("all", "com.tr"));
    }};

    public static Predicate<EntryWithFrom> fromPredicate(@NotNull LocalDateTime dateTime) {
        return e -> e.getFrom() == null || e.getFrom().isBefore(dateTime);
    }

    public static Predicate<EntryWithTill> tillPredicate(@NotNull LocalDateTime dateTime) {
        return e -> e.getTill() == null || e.getTill().isAfter(dateTime);
    }

    public static Predicate<EntryWithWeekDay> weekDayPredicate(@NotNull String weekDay) {
        return e -> e.getWeekDay().contains(weekDay);
    }

    public static Predicate<EntryWithId> id(@NotNull String id) {
        return e -> id.equals(e.getId());
    }

    public static Predicate<EntryWithLang> lang(@NotNull String lang) {
        return e -> lang.equals(e.getLang()) || "all".equals(e.getLang());
    }

    public static Predicate<EntryWithDomain> domain(@NotNull String domain) {
        return e -> DOMAIN_IN_DOMAIN_MAP.getOrDefault(domain, new ArrayList<>()).contains(e.getDomain());
    }

    public static Predicate<EntryWithContent> content(@NotNull String content) {
        return e -> content.equals(e.getContent()) || "all".equals(e.getContent());
    }

    public static Predicate<EntryWithGeo> geo(int geoId) {
        return e -> isGeoIdIn(geoId, e.getGeo().getRegion().getRegionId());
    }

    public static boolean isGeoIdIn(int childId, int parentId) {
        return new GeobaseRegion(childId).isIn(parentId);
    }

//    public static Predicate<EntryWithGeos> geos(int geoId) {
//        return e -> !e.getGeos().stream().filter(geo -> geo < 0).anyMatch(geo -> isGeoIdIn(geoId, abs(geo))) &&
//                e.getGeos().stream().filter(geo -> geo > 0).anyMatch(geo -> isGeoIdIn(geoId, geo));
//    }

    public static Predicate<EntryWithMordatype> mordatype(@NotNull String mordatype) {
        return e -> mordatype.equals(e.getMordatype()) || "all".equals(e.getMordatype());
    }

    public static Predicate<EntryWithPlatform> platform(@NotNull String platform) {
        return e -> e.getPlatform().contains(platform);
    }
}
