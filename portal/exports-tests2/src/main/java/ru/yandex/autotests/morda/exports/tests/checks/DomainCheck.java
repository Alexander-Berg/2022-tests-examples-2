package ru.yandex.autotests.morda.exports.tests.checks;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.function.Function;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.endsWith;
import static ru.yandex.autotests.morda.exports.filters.MordaExportFilters.isGeoIdIn;
import static ru.yandex.autotests.morda.region.Region.BELARUS;
import static ru.yandex.autotests.morda.region.Region.KAZAKHSTAN;
import static ru.yandex.autotests.morda.region.Region.KRIM;
import static ru.yandex.autotests.morda.region.Region.RUSSIA;
import static ru.yandex.autotests.morda.region.Region.UKRAINE;
import static ru.yandex.autotests.morda.exports.tests.utils.ExportUtils.normalizeUrl;

/**
 * User: asamar
 * Date: 14.08.2015.
 */
public class DomainCheck<T> extends ExportCheck<T> {

    private DomainCheck(String name,
                        Function<T, String> urlProvider,
                        Function<T, Integer> regionProvider) {
        super(
                format("\"%s\" domain check", name),
                e -> checkDomain(urlProvider.apply(e), regionProvider.apply(e))
        );
    }

    public static <T> DomainCheck<T> domain(String field,
                                            Function<T, String> urlProvider,
                                            Function<T, Integer> regionProvider) {
        return new DomainCheck<>(field, urlProvider, regionProvider);
    }

    public static void checkDomain(String url, int regionId) {
        String host = null;
        try {
            host = new URL(normalizeUrl(url)).getHost();
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }

        if (isGeoIdIn(regionId, RUSSIA.getId())) {
            if (isGeoIdIn(regionId, KRIM.getId())) {
                assertThat(url, host, anyOf(endsWith("ru"), endsWith("ua")));
            } else {
                assertThat(url, host, endsWith("ru"));
            }
        } else if (isGeoIdIn(regionId, UKRAINE.getId())) {
            assertThat(url, host, anyOf(endsWith("ru"), endsWith("ua")));
        } else if (isGeoIdIn(regionId, BELARUS.getId())) {
            assertThat(url, host, anyOf(endsWith("ru"), endsWith("by")));
        } else if (isGeoIdIn(regionId, KAZAKHSTAN.getId())) {
            assertThat(url, host, anyOf(endsWith("ru"), endsWith("kz")));
        }
    }
}
