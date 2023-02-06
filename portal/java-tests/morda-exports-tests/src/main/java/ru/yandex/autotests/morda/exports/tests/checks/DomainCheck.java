package ru.yandex.autotests.morda.exports.tests.checks;

import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;
import ru.yandex.geobase.regions.Countries;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.function.Function;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.endsWith;
import static ru.yandex.autotests.morda.exports.tests.utils.ExportUtils.normalizeUrl;

/**
 * User: asamar
 * Date: 14.08.2015.
 */
public class DomainCheck<T> extends ExportCheck<T> {

    private DomainCheck(String name,
                        Function<T, String> urlProvider,
                        Function<T, MordaGeoFilter> regionProvider) {
        super(
                format("\"%s\" domain check", name),
                e -> checkDomain(urlProvider.apply(e), regionProvider.apply(e))
        );
    }

    public static <T> DomainCheck<T> domain(String field,
                                            Function<T, String> urlProvider,
                                            Function<T, MordaGeoFilter> regionProvider) {
        return new DomainCheck<>(field, urlProvider, regionProvider);
    }

    public static void checkDomain(String url, MordaGeoFilter geoFilter) {
        GeobaseRegion region = geoFilter.getRegion();
        String host = null;
        try {
            host = new URL(normalizeUrl(url)).getHost();
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }

        if (region.isIn(Countries.RUSSIA)) {
            if (region.isIn(Russia.REPUBLIC_OF_CRIMEA)) {
                assertThat(url, host, anyOf(endsWith("ru"), endsWith("ua")));
            } else {
                assertThat(url, host, endsWith("ru"));
            }
        } else if (region.isIn(Countries.UKRAINE)) {
            assertThat(url, host, anyOf(endsWith("ru"), endsWith("ua")));
        } else if (region.isIn(Countries.BELARUS)) {
            assertThat(url, host, anyOf(endsWith("ru"), endsWith("by")));
        } else if (region.isIn(Countries.KAZAKHSTAN)) {
            assertThat(url, host, anyOf(endsWith("ru"), endsWith("kz")));
        }
    }
}
