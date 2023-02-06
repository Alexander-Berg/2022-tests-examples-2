package ru.yandex.autotests.morda.exports.filters;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithGeo;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.function.Predicate;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/06/16
 */
public class MordaGeoFilter {
    private static final Logger LOGGER = Logger.getLogger(MordaGeoFilter.class);

    private GeobaseRegion region;

    public MordaGeoFilter(int parentId) {
        this(new GeobaseRegion(parentId));
    }

    public MordaGeoFilter(GeobaseRegion parentRegion) {
        this.region = parentRegion;
    }

    public boolean matches(int geoId) {
        return matches(new GeobaseRegion(geoId));
    }

    public boolean matches(GeobaseRegion region) {
        if (region == null) {
            return false;
        }
        return region.isIn(this.region);
    }

    public static Predicate<EntryWithGeo> filter(int geoId) {
        return e -> e.getGeo().matches(geoId);
    }

    public static Predicate<EntryWithGeo> filter(GeobaseRegion region) {
        return e -> e.getGeo().matches(region);
    }

    public GeobaseRegion getRegion() {
        return region;
    }

    @Override
    public String toString() {
        return region.toString();
    }
}
