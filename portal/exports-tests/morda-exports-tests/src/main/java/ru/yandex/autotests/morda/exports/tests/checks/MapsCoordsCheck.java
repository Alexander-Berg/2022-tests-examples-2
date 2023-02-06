package ru.yandex.autotests.morda.exports.tests.checks;

import ru.yandex.autotests.morda.exports.tests.utils.ExportUtils;
import ru.yandex.autotests.morda.exports.tests.utils.MapsArea;
import ru.yandex.autotests.morda.exports.tests.utils.MapsUtils;

import java.util.function.Function;
import java.util.function.Predicate;

import static java.lang.String.format;
import static org.junit.Assert.assertTrue;

/**
 * User: asamar
 * Date: 17.08.2015.
 */
public class MapsCoordsCheck<T> extends ExportCheck<T> {

    private MapsCoordsCheck(String name,
                            Function<T, String> urlProvider,
                            Function<T, Integer> geoProvider,
                            Predicate<T> condition) {
        super(format("\"%s\" maps coords check", name),
                e -> checkMapsCoords(geoProvider.apply(e), ExportUtils.normalizeUrl(urlProvider.apply(e))),
                condition);
    }

    public static <T> MapsCoordsCheck<T> mapsCoords(String name,
                                                   Function<T, String> urlProvider,
                                                   Function<T, Integer> geoProvider
                                                   ){
        return mapsCoords(name, urlProvider, geoProvider, e -> true);
    }

    public static <T> MapsCoordsCheck<T> mapsCoords(String name,
                                                   Function<T, String> urlProvider,
                                                   Function<T, Integer> geoProvider,
                                                   Predicate<T> condition) {
        return new MapsCoordsCheck<>(name, urlProvider, geoProvider, condition);
    }

    public static void checkMapsCoords(int geoId, String url) {
        MapsArea urlArea = MapsUtils.getMapsArea(url);
        MapsArea baseArea = MapsUtils.getLocation(geoId);
        assertTrue("Регионы в ссылке и геобазе не пересекаются. GeoId: " +
                        geoId + ".\nUrlArea = " + urlArea + "\nGeobaseArea = " + baseArea,
                urlArea.intersects(baseArea));
    }

}
