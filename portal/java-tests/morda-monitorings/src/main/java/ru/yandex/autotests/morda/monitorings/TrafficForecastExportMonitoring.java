package ru.yandex.autotests.morda.monitorings;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.restassured.requests.TypifiedRestAssuredGetRequest;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.MonitoringNotifierRule;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetric;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.time.LocalTime;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.Assert.fail;
import static ru.yandex.qatools.monitoring.MonitoringNotifierRule.notifierRule;

@Aqua.Test(title = "Прогноз пробок")
@Features("Traffic")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_traffic")
public class TrafficForecastExportMonitoring {

    private static final String TRAFFIC_FORECAST_URL = "http://wfarm.yandex.net/exports/traffic-forecast.json";
    @Rule
    @ClassRule
    public static MonitoringNotifierRule notifierRule = notifierRule();

    @Rule
    public AllureLoggingRule loggingRule = new AllureLoggingRule();
    private GeobaseRegion region;
    private Map<Integer, TrafficForecastRegionForecast> export;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<GeobaseRegion> data() {
        return asList(Russia.MOSCOW, Russia.SAINT_PETERSBURG, Ukraine.KYIV);
    }

    public TrafficForecastExportMonitoring(GeobaseRegion region) {
        this.region = region;
    }

    @Before
    public void getExport() {
        try {
            JsonNode export = new TypifiedRestAssuredGetRequest<>(JsonNode.class, TRAFFIC_FORECAST_URL).read();

            ObjectMapper objectMapper = new ObjectMapper();

            this.export = objectMapper.readValue(export.traverse(),
                    objectMapper.getTypeFactory().constructMapType(HashMap.class, Integer.class, TrafficForecastRegionForecast.class));

        } catch (Exception e) {
            fail("Failed to get traffic-forecast export:\n" + e.getMessage());
        }
    }

    @Test
    @GolemEvent("traffic_forecast")
    @YasmSignal(signal = "morda_traffic_forecast_%s_tttt")
    public void trafficForecastExport() throws JsonProcessingException {
        LocalTime time = Russia.MOSCOW.getTime();

        TrafficForecastRegionForecast forecastRegionForecast = export.get(region.getRegionId());
        assertThat("Not found forecast data for " + region, forecastRegionForecast, notNullValue());
        if (time.isAfter(LocalTime.of(8, 10)) && time.isBefore(LocalTime.of(22, 0))) {
            assertThat("No forecast for " + region,
                    forecastRegionForecast.getJams().entrySet(), hasSize(greaterThan(0)));
        }
    }

    private static class TrafficForecastRegionForecast {
        public long timestamp;
        public Map<String, Object> jams;

        public Map<String, Object> getJams() {
            return jams;
        }

        public void setJams(Map<String, Object> jams) {
            this.jams = jams;
        }

        public long getTimestamp() {
            return timestamp;
        }

        public void setTimestamp(long timestamp) {
            this.timestamp = timestamp;
        }
    }

}
