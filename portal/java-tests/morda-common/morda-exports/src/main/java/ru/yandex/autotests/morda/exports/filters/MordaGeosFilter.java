package ru.yandex.autotests.morda.exports.filters;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithGeos;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.List;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.joining;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/06/16
 */
public class MordaGeosFilter {
    private static final Logger LOGGER = Logger.getLogger(MordaGeosFilter.class);

    private List<GeobaseRegion> regions;

    public MordaGeosFilter(List<Integer> parentIds) {
        this.regions = parentIds.stream().map(GeobaseRegion::new).collect(Collectors.toList());
    }

    public boolean matches(int geoId) {
        return matches(new GeobaseRegion(geoId));
    }

    public boolean matches(GeobaseRegion region) {
        if (region == null) {
            return false;
        }
        return regions.stream().anyMatch(region::isIn);
    }

    public static Predicate<EntryWithGeos> filter(int geoId) {
        return e -> e.getGeos().matches(geoId);
    }

    public static Predicate<EntryWithGeos> filter(GeobaseRegion region) {
        return e -> e.getGeos().matches(region);
    }

    public List<GeobaseRegion> getRegions() {
        return regions;
    }

    @Override
    public String toString() {
        return regions.stream()
                .map(e -> String.valueOf(e.getRegionId()))
                .collect(joining(", "));
    }
}
