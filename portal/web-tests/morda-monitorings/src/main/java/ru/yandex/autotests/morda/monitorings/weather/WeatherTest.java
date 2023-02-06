package ru.yandex.autotests.morda.monitorings.weather;

import org.apache.commons.httpclient.util.HttpURLConnection;
import org.joda.time.LocalDateTime;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.weather.Weather;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.TimeUtils.parseHiddenTime;
import static ru.yandex.autotests.mordabackend.weather.WeatherUtils.TEMPERATURE_MATCHER;
import static ru.yandex.autotests.mordabackend.weather.WeatherUtils.getT2NameMatcher;
import static ru.yandex.autotests.mordabackend.weather.WeatherUtils.getT3NameMatcher;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.region.Region.DONECK;

@Aqua.Test(title = "Погода")
@Features("Погода")
@RunWith(Parameterized.class)
public class WeatherTest {

    private static final MonitoringProperties CONFIG = new MonitoringProperties();

    @Rule
    public MordaMonitoringsRule rule = new MordaMonitoringsRule();

    @Parameterized.Parameters(name = "Weather block in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
//                ASTANA, ALMATY, CHEBOKSARI, CHELYABINSK, DNEPROPETROVSK,
                DONECK
//                , EKATERINBURG,
//                HABAROVSK, IRKUTSK, HARKOV, KALININGRAD, KRASNODAR, KRASNOYARSK, KIEV, KAZAN,
//                MINSK, MURMANSK, MOSCOW, NIZHNIY_NOVGOROD, NOVOSIBIRSK, PERM, PETROZAVODSK,
//                ROSTOV_NA_DONU, SEVASTOPOL, SIMFEROPOL, SAMARA, SANKT_PETERBURG, TOMSK, TOLYATTI,
//                TULA, UFA, VLADIKAVKAZ, VLADIVOSTOK, VOLGOGRAD, VORONEZH, YAROSLAVL, DUBNA
        ));
    }

    private Region region;
    private Language language = RU;
    private Cleanvars cleanvars;
    private Client client;

    public WeatherTest(Region region) throws IOException {
        this.region = region;
        this.client = MordaClient.getJsonEnabledClient();

        MordaClient mordaClient = new MordaClient(CONFIG.getMordaEnv(), region.getDomain());

        client.target(mordaClient.getMordaHost()).request().buildGet().invoke().close();

        mordaClient.rapidoActions(client)
                .getResponse("common", new CookieHeader(new Cookie(CookieName.YANDEX_GID, region.getRegionId())), null, null, null);

        Cleanvars common = mordaClient.rapidoActions(client)
                .get("common", new CookieHeader(new Cookie(CookieName.YANDEX_GID, region.getRegionId())), null, null, null);

        mordaClient.tuneActions(client).setLanguage(common.getSk(), language, mordaClient.getMordaHost());

        mordaClient.tuneActions(client).setRegion(region);

        String response = mordaClient
                .rapidoActions(client)
                .getResponse("weather", null, null, null, null)
                .readEntity(String.class);

        this.cleanvars = MordaClient.getObjectMapper().readValue(response, Cleanvars.class);

        rule.addMeta("json", response);
    }

//    @Test
    public void weatherIsShown() {
        shouldHaveParameter("Погода отсутствует в " + region.getName(),
                cleanvars.getWeather(), having(on(Weather.class).getProcessed(), equalTo(1)));

        shouldHaveParameter("Погода отсутствует в " + region.getName(),
                cleanvars.getWeather(), having(on(Weather.class).getShow(), equalTo(1)));
    }

//    @Test
    public void weatherResponse() throws IOException {
        ifWeatherShown();

        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getHref(), notNullValue()));
        shouldHaveResponseCode(client, cleanvars.getWeather().getHref(), equalTo(HttpURLConnection.HTTP_OK));

        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getNoticeHref(), notNullValue()));
        shouldHaveResponseCode(client, cleanvars.getWeather().getNoticeHref(), equalTo(HttpURLConnection.HTTP_OK));

    }

    @Test
    public void weatherForecast() throws IOException {
        ifWeatherShown();

        LocalDateTime hiddenTime = parseHiddenTime(cleanvars.getHiddenTime());

        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT1(), TEMPERATURE_MATCHER));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT2(), TEMPERATURE_MATCHER));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT2Name(),
                getT2NameMatcher(hiddenTime.getHourOfDay(), language)));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT3(), TEMPERATURE_MATCHER));
        shouldHaveParameter(cleanvars.getWeather(), having(on(Weather.class).getT3Name(),
                getT3NameMatcher(hiddenTime.getHourOfDay(), language)));

    }

    private void ifWeatherShown() {
        assumeThat("Погода отсутствует в " + region.getName(), cleanvars.getWeather(),
                having(on(Weather.class).getShow(), equalTo(1)));
    }

}
