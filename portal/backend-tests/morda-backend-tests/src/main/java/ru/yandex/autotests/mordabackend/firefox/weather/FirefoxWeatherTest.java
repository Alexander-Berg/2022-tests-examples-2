package ru.yandex.autotests.mordabackend.firefox.weather;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.weather.Weather;
import ru.yandex.autotests.mordabackend.beans.weather.Xiva;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesV122ParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.text.ParseException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.lang.Integer.parseInt;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.weather.WeatherUtils.*;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: eoff
 * Date: 20.06.2014
 */
@Aqua.Test(title = "Firefox Weather Block")
@Features("Firefox")
@Stories("Firefox Weather Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class FirefoxWeatherTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(new BaseProperties.MordaEnv(CONFIG.getMordaEnv().getEnv().replace("www-", "firefox-")),
                    RU, UA, COM_TR)
                    .withLanguages(Language.RU, Language.UK, Language.BE, Language.KK, Language.TT)
                    .withUserAgents(FF_34)
                    .withParameterProvider(new ServicesV122ParameterProvider("pogoda"))
                    .withCleanvarsBlocks(WEATHER, LOCAL, WSTEMP);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final Language language;
    private final UserAgent userAgent;
    private final ServicesV122Entry servicesV122Entry;

    public FirefoxWeatherTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                              Language language, UserAgent userAgent, ServicesV122Entry servicesV122Entry) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.servicesV122Entry = servicesV122Entry;
    }

    @Test
    public void showFlag() throws IOException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() throws IOException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getProcessed(), equalTo(1)));
    }

    @Test
    public void weatherCurrent() throws IOException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT1(), TEMPERATURE_MATCHER));
    }

    @Test
    public void weatherForecast() throws IOException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT2(), TEMPERATURE_MATCHER));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT3(), TEMPERATURE_MATCHER));
    }

    @Test
    public void weatherForecastNames() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT2Name(),
                getT2NameMatcher(cleanvars.getLocal().getHour(), language)));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT3Name(),
                getT3NameMatcher(cleanvars.getLocal().getHour(), language)));
    }

    @Test
    public void weatherGeoId() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getGeoid(),
                equalTo(getWeatherGeoId(region))));
    }

    @Test
    public void xivasParameter() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getXivas(),
                hasSize(1)));
        shouldHaveParameter(cleanvars.getWeather().getXivas().get(0), having(on(Xiva.class).getKey(),
                equalTo(getWeatherGeoId(region))));
        shouldHaveParameter(cleanvars.getWeather().getXivas().get(0), having(on(Xiva.class).getCh(),
                anyOf(
                        equalTo("weather_v2"),
                        equalTo("weather")
                )));
    }

    @Test
    public void mobUrl() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getMoburl(),
                getFirefoxUrlMatcher(servicesV122Entry, region, userAgent)));
        shouldHaveResponseCode(client, cleanvars.getWeather().getMoburl(), userAgent, equalTo(200));
    }

    @Test
    public void weatherUrl() throws IOException, ParseException {
        assumeThat("Unused on pda and touch", userAgent.isMobile(), equalTo(false));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getUrl(),
                getFirefoxUrlMatcher(servicesV122Entry, region, userAgent)));
        addLink(cleanvars.getWeather().getUrl(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getWeather().getUrl(), userAgent, equalTo(200));
    }

    @Test
    public void weatherHref() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getHref(),
                getFirefoxUrlMatcher(servicesV122Entry, region, userAgent)));
        addLink(cleanvars.getWeather().getHref(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getWeather().getHref(), userAgent, equalTo(200));
    }

    @Test
    public void weatherNoticeHref() throws IOException, ParseException {
        assumeThat("Unused on pda and touch", userAgent.isMobile(), equalTo(false));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getNoticeHref(),
                getFirefoxUrlMatcher(servicesV122Entry, region, userAgent)));
        shouldHaveResponseCode(client, cleanvars.getWeather().getNoticeHref(), userAgent, equalTo(200));
    }

    @Test
    public void wsTemp() throws IOException, ParseException {
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWSTemp(),
                equalTo(parseInt(cleanvars.getWeather().getT1().replace('−', '-')))));
    }
}
