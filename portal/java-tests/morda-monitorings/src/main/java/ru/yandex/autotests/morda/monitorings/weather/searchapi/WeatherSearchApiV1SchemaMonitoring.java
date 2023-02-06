package ru.yandex.autotests.morda.monitorings.weather.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiV1SchemaMonitoring;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetricPrefix;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.WEATHER;

/**
 * User: asamar
 * Date: 27.06.16
 */
@Aqua.Test(title = "Weather search api schema monitoring")
@Features({"Search-api", "Weather"})
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_weather")
@GraphiteMetricPrefix("weather.apisearch_v1")
public class WeatherSearchApiV1SchemaMonitoring extends BaseSearchApiV1SchemaMonitoring {

    public WeatherSearchApiV1SchemaMonitoring(SearchApiRequestData requestData) {
        super(requestData);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        List<SearchApiRequestData> data = new ArrayList<>();

        for (GeobaseRegion region : asList(
                Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.VLADIVOSTOK,
                Belarus.MINSK,
                Ukraine.KYIV,
                Kazakhstan.ALMATY
        )) {

            data.add(new SearchApiRequestData()
                    .setGeo(region)
                    .setLanguage(getRandomLanguage())
                    .setBlock(WEATHER)
            );
        }
        return data;
    }
}
