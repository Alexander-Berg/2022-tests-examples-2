package ru.yandex.autotests.weather.tests.consistency;

import net.lightbody.bmp.core.har.Har;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.logging.LogEntry;
import org.openqa.selenium.logging.LogType;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.utils.matchers.StaticDownloadedMatcher;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.core.UriBuilder;
import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Level;
import java.util.stream.Collectors;

import static java.lang.Thread.sleep;
import static java.util.Arrays.asList;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.collection.IsCollectionWithSize.hasSize;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

/**
 * User: asamar
 * Date: 20.01.17
 */
@Aqua.Test(title = "Desktop consistency")
@RunWith(Parameterized.class)
@Features("Consistency")
public class WeatherDesktopConsistencyTest {
    private static final WeatherWebTestsProperties CONFIG = new WeatherWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<URI> data() {
        List<URI> data = new ArrayList<>();

        String scheme = CONFIG.getWeatherScheme();
        String environment = CONFIG.getWeatherEnvironment();

        for (String domain : asList(".ru", ".ua", ".kz", ".by")) {
            URI baseUri = UriBuilder.fromUri("{scheme}://{env}.yandex{domain}/pogoda")
                    .build(scheme, environment, domain);

            data.add(fromUri(baseUri).path("moscow").build());
            data.add(fromUri(baseUri).path("london").build());
            data.add(fromUri(baseUri).path("moscow/details").build());
            data.add(fromUri(baseUri).path("moscow/month").build());
            data.add(fromUri(baseUri).path("moscow/month/february").build());
            data.add(fromUri(baseUri).path("moscow/nowcast").build());
            data.add(fromUri(baseUri).path("moscow/maps").build());
            data.add(fromUri(baseUri).path("moscow/choose").build());
            data.add(fromUri(baseUri).path("region/225").build());
//            data.add(fromUri(baseUri).path("meteum").build());
            data.add(fromUri(baseUri).path("kyiv/details").fragment("30").build());
            data.add(fromUri(baseUri).path("moscow/informer").build());
            data.add(fromUri(baseUri)
                    .path("moscow")
                    .path("maps")
                    .queryParam("region", "ru-north-west")
                    .build());
            data.add(fromUri(baseUri)
                    .path("search")
                    .queryParam("request", "f")
                    .queryParam("suggest_reqid", "207167371146191839222884488177864")
                    .build());

            // с координатами
            data.add(fromUri(baseUri)
                    .queryParam("lat", "44.016815")
                    .queryParam("lon", "39.234738")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow/details")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow/month")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow/month/august")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow/nowcast")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
            data.add(fromUri(baseUri)
                    .path("moscow/maps")
                    .queryParam("lat", "55.640728")
                    .queryParam("lon", "37.6078911")
                    .build());
        }

        // https://p.ya.ru testing
        URI yaruUri = UriBuilder.fromUri("{scheme}://mini.pogoda.nodejs.weather-test.yandex.ru")
                .path("moscow")
                .queryParam("lat", "55.7348213")
                .queryParam("lon", "37.5858192")
                .build(scheme);
        data.add(yaruUri);

        URI comTrUri = UriBuilder.fromUri("{scheme}://{env}.yandex.com.tr/hava")
                .build(scheme, environment);

        data.add(fromUri(comTrUri).path("moscow").build());
        data.add(fromUri(comTrUri).path("london").build());
        data.add(fromUri(comTrUri).path("istanbul/details").build());
        data.add(fromUri(comTrUri).path("istanbul/month").build());
        data.add(fromUri(comTrUri).path("istanbul/month/february").build());
        data.add(fromUri(comTrUri).path("istanbul/choose").build());
        data.add(fromUri(comTrUri).path("region/983").build());
        data.add(fromUri(comTrUri).path("meteum").build());
        data.add(fromUri(comTrUri).path("istanbul/details").fragment("30").build());
        data.add(fromUri(comTrUri)
                .path("search")
                .queryParam("request", "ank")
                .queryParam("suggest_reqid", "591240054148551774714996663876089")
                .build());

        // с координатами
        data.add(fromUri(comTrUri)
                .queryParam("lat", "44.016815")
                .queryParam("lon", "39.234738")
                .build());
        data.add(fromUri(comTrUri)
                .path("fatih")
                .queryParam("lat", "41.008925")
                .queryParam("lon", "28.967111")
                .build());
        data.add(fromUri(comTrUri)
                .path("fatih/details")
                .queryParam("lat", "41.008925")
                .queryParam("lon", "28.967111")
                .build());
        data.add(fromUri(comTrUri)
                .path("fatih/month")
                .queryParam("lat", "41.008925")
                .queryParam("lon", "28.967111")
                .build());
        data.add(fromUri(comTrUri)
                .path("fatih/month/august")
                .queryParam("lat", "41.008925")
                .queryParam("lon", "28.967111")
                .build());

        //метеум только на .ru!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        data.add(fromUri("{scheme}://{env}.yandex.ru/pogoda/meteum")
                .build(scheme, environment));

        return data;
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private URI uri;

    public WeatherDesktopConsistencyTest(URI uri) {
        this.uri = uri;
        this.mordaAllureBaseRule = new MordaAllureBaseRule()
                .withProxyAction(addHar("js-errors"));
        this.driver = mordaAllureBaseRule.getDriver();
    }

    @Before
    public void setUp() throws InterruptedException {
        NavigationSteps.open(driver, uri);
        sleep(2000);
    }

    @Test
    public void noJSErrors() throws IOException {
        List<LogEntry> severeLogs = driver.manage().logs().get(LogType.BROWSER).getAll().stream()
                .filter(e -> !e.getMessage().contains("NS_ERROR_ILLEGAL_VALUE")
                        && !e.getMessage().contains("NS_ERROR_FAILURE")
                        && e.getLevel().equals(Level.SEVERE))
                .collect(Collectors.toList());

        severeLogs.removeIf(e -> e.getMessage().contains("https://music.yandex.ru"));
        severeLogs.removeIf(e -> e.getMessage().contains("https://ads.adfox.ru/"));
        severeLogs.removeIf(e -> e.getMessage().contains("an.yandex.ru"));
        severeLogs.removeIf(e -> e.getMessage().contains("front/nowcast-timeline"));
        severeLogs.removeIf(e -> e.getMessage().contains("https://mc.yandex.ru/metrika/watch.js"));
        severeLogs.removeIf(e -> e.getMessage().contains("chrome-extension"));


        assertThat("Detected " + severeLogs.size() + " js-errors: " + severeLogs, severeLogs, hasSize(0));
    }

    @Test
    public void staticIsOk() {
        Har har = mordaAllureBaseRule.getProxyServer().getHar();
        har.getLog().getEntries().removeIf(e -> e.getRequest().getUrl().contains("favicon.ico"));
        har.getLog().getEntries().removeIf(e -> e.getRequest().getUrl().contains("https://ads.adfox.ru/"));
        har.getLog().getEntries().removeIf(e -> e.getRequest().getUrl().contains("https://an.yandex.ru/"));
        har.getLog().getEntries().removeIf(e -> e.getRequest().getUrl().contains("front/nowcast-timeline"));

        assertThat(uri.toString(), har, StaticDownloadedMatcher.staticDownloaded());
    }
}
