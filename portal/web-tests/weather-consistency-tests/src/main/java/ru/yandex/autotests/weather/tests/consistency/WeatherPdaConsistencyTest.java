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
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;
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
 * Date: 23.01.17
 */
@Aqua.Test(title = "Pda consistency")
@RunWith(Parameterized.class)
@Features("Consistency")
public class WeatherPdaConsistencyTest {
    private static final WeatherWebTestsProperties CONFIG = new WeatherWebTestsProperties();
    private static final String POGODA = "pogoda";
    private static final String SPB = "saint-petersburg";

    @Parameterized.Parameters(name = "{0}")
    public static Collection<URI> data() {
        List<URI> data = new ArrayList<>();

        String scheme = CONFIG.getWeatherScheme();
        String environment = CONFIG.getWeatherEnvironment();

        for (String domain : asList(".ru",".ua",".kz",".by",".com.tr")) {

            URI baseUri = UriBuilder.fromUri("{scheme}://{env}.yandex{domain}/pogoda")
                    .build(scheme, environment, domain);

            if (".com.tr".equals(domain)) {
                baseUri = UriBuilder.fromUri("{scheme}://{env}.yandex{domain}/hava")
                        .build(scheme, environment, domain);
            }

            data.add(fromUri(baseUri)
                    .path(SPB)
                    .build());
            data.add(fromUri(baseUri)
                    .path(SPB)
                    .queryParam("lat", "59.95940399169922")
                    .queryParam("lon", "30.40688514709473")
                    .build());
            data.add(fromUri(baseUri)
                    .path("search")
                    .queryParam("request", "п")
                    .build());
        }
        return data;
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private URI uri;

    public WeatherPdaConsistencyTest(URI uri) {
        this.uri = uri;
        this.mordaAllureBaseRule = new MordaAllureBaseRule()
                .replaceProxyAction(UserAgentAction.class, CONFIG.getWeatherUserAgentPda())
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

        severeLogs.removeIf(e -> e.getMessage().contains("an.yandex.ru"));

        assertThat("Detected " + severeLogs.size() + " js-errors: " + severeLogs, severeLogs, hasSize(0));
    }

    @Test
    public void staticIsOk() {
        Har har = mordaAllureBaseRule.getProxyServer().getHar();
        har.getLog().getEntries().removeIf(e -> e.getRequest().getUrl().contains("favicon.ico"));
        har.getLog().getEntries().removeIf(e -> e.getRequest().getUrl().contains("an.yandex.ru"));

        assertThat(uri.toString(), har, StaticDownloadedMatcher.staticDownloaded());
    }
}
