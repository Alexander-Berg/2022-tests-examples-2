package ru.yandex.autotests.morda.tests;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * User: asamar
 * Date: 25.01.17
 */
@Resource.Classpath("weather-pages.properties")
public class WeatherPagesProperties {

    public WeatherPagesProperties() {
        PropertyLoader.populate(this);
    }

    @Property("weather.scheme")
    private String weatherScheme;

    @Property("weather.environment")
    private String weatherEnvironment;

    public String getWeatherScheme() {
        return weatherScheme;
    }

    public String getWeatherEnvironment() {
        return weatherEnvironment;
    }
}
