package ru.yandex.autotests.morda.exports.tests.checks;

import java.util.function.Function;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isIn;
import static ru.yandex.autotests.morda.exports.filters.MordaExportFilters.DOMAIN_IN_DOMAIN_MAP;
import static ru.yandex.autotests.morda.exports.filters.MordaExportFilters.isGeoIdIn;
import static ru.yandex.autotests.morda.region.Region.BELARUS;
import static ru.yandex.autotests.morda.region.Region.KAZAKHSTAN;
import static ru.yandex.autotests.morda.region.Region.KRIM;
import static ru.yandex.autotests.morda.region.Region.RUSSIA;
import static ru.yandex.autotests.morda.region.Region.UKRAINE;

/**
 * User: asamar
 * Date: 17.08.2015.
 */
public class RegionTargetingCheck<T> extends ExportCheck<T> {

    private RegionTargetingCheck(String name,
                                 Function<T, String> domainProvider,
                                 Function<T, Integer> geoProvider
    ) {
        super(
                format("\"%s\" region targeting", name),
                e -> checkRegionInDomain(geoProvider.apply(e), domainProvider.apply(e))
        );
    }

    public static <T> RegionTargetingCheck<T> regionTargeting(String name,
                                                              Function<T, String> domainProvider,
                                                              Function<T, Integer> geoProvider) {
        return new RegionTargetingCheck<>(name, domainProvider, geoProvider);
    }

    public static void checkRegionInDomain(int regionId, String domain) {
        String errorMessage = "В списке родителей нет нужного региона для gid=" + regionId;

        if (isGeoIdIn(regionId, RUSSIA.getId())) {
            if (isGeoIdIn(regionId, KRIM.getId())) {
                assertThat(errorMessage, domain, anyOf(
                        isIn(DOMAIN_IN_DOMAIN_MAP.get("ru")),
                        equalTo("ua")
                ));
            } else {
                assertThat(errorMessage, domain, isIn(DOMAIN_IN_DOMAIN_MAP.get("ru")));
            }
        } else if (isGeoIdIn(regionId, UKRAINE.getId())) {
            assertThat(errorMessage, domain, isIn(DOMAIN_IN_DOMAIN_MAP.get("ua")));

        } else if (isGeoIdIn(regionId, BELARUS.getId())) {
            assertThat(errorMessage, domain, isIn(DOMAIN_IN_DOMAIN_MAP.get("by")));

        } else if (isGeoIdIn(regionId, KAZAKHSTAN.getId())) {
            assertThat(errorMessage, domain, isIn(DOMAIN_IN_DOMAIN_MAP.get("kz")));
        }
    }
}
