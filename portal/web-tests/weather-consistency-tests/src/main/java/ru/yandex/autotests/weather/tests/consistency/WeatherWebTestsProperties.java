package ru.yandex.autotests.weather.tests.consistency;

import org.apache.commons.beanutils.ConvertUtils;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.util.List;

/**
 * User: asamar
 * Date: 20.01.17
 */
@Resource.Classpath("weather-web-tests.properties")
public class WeatherWebTestsProperties {

    public WeatherWebTestsProperties() {
        ConvertUtils.register(new ListConverter(", "), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    @Property("weather.scheme")
    private String weatherScheme;

    @Property("weather.environment")
    private String weatherEnvironment;

    @Property("weather.useragent.touch.iphone")
    private String weatherUserAgentTouchIphone;

    @Property("weather.useragent.touch.wp")
    private String weatherUserAgentTouchWp;

    @Property("weather.useragent.pda")
    private String weatherUserAgentPda;

    public String getWeatherScheme() {
        return weatherScheme;
    }

    public String getWeatherEnvironment() {
        return weatherEnvironment;
    }

    public String getWeatherUserAgentTouchIphone() {
        return weatherUserAgentTouchIphone;
    }

    public String getWeatherUserAgentTouchWp() {
        return weatherUserAgentTouchWp;
    }

    public String getWeatherUserAgentPda() {
        return weatherUserAgentPda;
    }
}
