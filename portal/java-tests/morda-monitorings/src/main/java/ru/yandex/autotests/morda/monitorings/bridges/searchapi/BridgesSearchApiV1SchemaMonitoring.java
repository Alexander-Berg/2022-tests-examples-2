package ru.yandex.autotests.morda.monitorings.bridges.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiV1SchemaMonitoring;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetricPrefix;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.BRIDGES;

/**
 * User: asamar
 * Date: 27.06.16
 */
@Aqua.Test(title = "Bridges search api schema monitoring")
@Features({"Search-api", "Bridges"})
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_bridges")
@GraphiteMetricPrefix("bridges.apisearch_v1")
public class BridgesSearchApiV1SchemaMonitoring extends BaseSearchApiV1SchemaMonitoring {

    public BridgesSearchApiV1SchemaMonitoring(SearchApiRequestData requestData) {
        super(requestData);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        List<SearchApiRequestData> data = new ArrayList<>();

        for (GeobaseRegion region : asList(Russia.SAINT_PETERSBURG)) {

            data.add(new SearchApiRequestData()
                    .setGeo(region)
                    .setLanguage(getRandomLanguage())
                    .setBlock(BRIDGES)
            );
        }
        return data;
    }
}
