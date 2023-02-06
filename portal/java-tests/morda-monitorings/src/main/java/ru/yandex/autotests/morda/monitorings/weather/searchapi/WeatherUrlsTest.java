package ru.yandex.autotests.morda.monitorings.weather.searchapi;

import org.apache.commons.lang3.RandomStringUtils;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.weather.WeatherApiV1;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.core.UriBuilder;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static ru.yandex.autotests.morda.api.search.SearchApiBlock.WEATHER;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.WEATHER_REGIONS;

/**
 * User: asamar
 * Date: 28.06.16
 */
@Aqua.Test(title = "Weather search api monitoring")
@Features({"Search-api", "Weather"})
@RunWith(Parameterized.class)
public class WeatherUrlsTest extends BaseSearchApiMonitoring<WeatherApiV1> {
    private WeatherApiV1 weather;

    public WeatherUrlsTest(MainMorda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        WEATHER_REGIONS.forEach(region -> data.add(desktopMain().region(region)));

        return data;
    }

    @Override
    protected WeatherApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();

        weather = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.WEATHER)
                .withGeo(morda.getRegion())
                .read()
                .getWeather();
        return weather;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return WEATHER;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();

        names.add(weather.getData().getT1().getUnit());
        names.add(String.valueOf(weather.getData().getT1().getValue()));
        names.add(weather.getData().getT2().getUnit());
        names.add(String.valueOf(weather.getData().getT2().getValue()));
        names.add(weather.getData().getT3().getUnit());
        names.add(String.valueOf(weather.getData().getT3().getValue()));

        names.add(weather.getData().getT2Name());
        names.add(weather.getData().getT3Name());

        weather.getData().getForecast().forEach(forecastItem -> {
            names.add(forecastItem.getDay().getUnit());
            names.add(String.valueOf(forecastItem.getDay().getValue()));
            names.add(forecastItem.getNight().getUnit());
            names.add(String.valueOf(forecastItem.getNight().getValue()));
        });

        weather.getData().getShortForecast().forEach(shortItem -> {
            names.add(shortItem.getText());
            names.add(shortItem.getName());
            names.add(shortItem.getTemp().getUnit());
            names.add(String.valueOf(shortItem.getTemp().getValue()));
        });

        weather.getData().getParts().forEach(part -> {
            names.add(part.getName());
            names.add(part.getTemp().getUnit());
            names.add(String.valueOf(part.getTemp().getValue()));
        });

        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        urls.addAll(weather.getData().getForecast()
                .stream()
                .collect(ArrayList<String>::new,
                        (list, forecast) -> {
                            list.add(forecast.getIcon());
                            list.add(forecast.getIconDaynight());
                        },
                        ArrayList::addAll));

        urls.addAll(weather.getData().getShortForecast()
                .stream()
                .collect(ArrayList<String>::new,
                        (list, forecast) -> {
                            list.add(forecast.getIcon());
                            list.add(forecast.getIconDaynight());
                        },
                        ArrayList::addAll));

        urls.addAll(weather.getData().getParts()
                .stream()
                .collect(ArrayList<String>::new,
                        (list, forecast) -> {
                            list.add(forecast.getIcon());
                            list.add(forecast.getIconDaynight());
                        },
                        ArrayList::addAll));

        urls.add(weather.getData().getIcon());
        urls.add(weather.getData().getUrl());
        urls.add(weather.getData().getNoticeUrl());

        return  Stream.of(urls.toArray(new String[0]))
                .map(e -> e.contains("yastatic")? e : UriBuilder.fromUri(e).queryParam("test_request_id",
                        RandomStringUtils.random(10, true, true) + "." + System.currentTimeMillis())
                        .build()
                        .toASCIIString()
                ).collect(Collectors.toList());
    }
}
