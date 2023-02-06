package ru.yandex.autotests.morda.exports.tests.checks;

import ru.yandex.autotests.morda.exports.filters.MordaDomainFilter;
import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;

import java.util.function.Function;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.Assume.assumeThat;

/**
 * User: asamar
 * Date: 17.08.2015.
 */
public class RegionTargetingCheck<T> extends ExportCheck<T> {

    private RegionTargetingCheck(String name,
                                 Function<T, MordaDomainFilter> domainProvider,
                                 Function<T, MordaGeoFilter> geoProvider
    ) {
        super(
                format("\"%s\" region targeting", name),
                e -> checkRegionInDomain(geoProvider.apply(e), domainProvider.apply(e))
        );
    }

    public static <T> RegionTargetingCheck<T> regionTargeting(String name,
                                                              Function<T, MordaDomainFilter> domainProvider,
                                                              Function<T, MordaGeoFilter> geoProvider) {
        return new RegionTargetingCheck<>(name, domainProvider, geoProvider);
    }

    public static void checkRegionInDomain(MordaGeoFilter geoFilter, MordaDomainFilter domain) {
        GeobaseRegion region = geoFilter.getRegion();
        assumeThat("Не надо проверять для geoId=10000", region.getRegionId(), not(equalTo(10000)));

        String errorMessage = "Неверный домен для \"" + region + "\": " + domain;

        if (region.isIn(Russia.REPUBLIC_OF_CRIMEA)) {
            assertThat(errorMessage, domain.matches(MordaDomain.RU) || domain.matches(MordaDomain.UA), is(true));
        } else {
            MordaDomain regionDomain = MordaDomain.fromString(region.getKubrDomain());
            assertThat(errorMessage, domain.matches(regionDomain), is(true));
        }
    }
}
