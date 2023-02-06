package ru.yandex.autotests.weather.tests.consistency;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.core.har.HarEntry;
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

import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Level;

import static java.lang.Thread.sleep;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.collection.IsCollectionWithSize.hasSize;
import static org.hamcrest.number.OrderingComparison.greaterThanOrEqualTo;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

/**
 * User: asamar
 * Date: 27.01.17
 */
@Aqua.Test(title = "500 consistency")
@RunWith(Parameterized.class)
@Features("Consistency")
public class Weather500ConsistencyTest {
    private static final WeatherWebTestsProperties CONFIG = new WeatherWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<URI> data() {
        List<URI> data = new ArrayList<>();

        String scheme = CONFIG.getWeatherScheme();
        String environment = CONFIG.getWeatherEnvironment();

        for (String domain : asList(".ru", ".ua", ".kz", ".by")) {

            URI uri = fromUri("{scheme}://{env}.yandex{domain}/pogoda/")
                    .build(scheme, environment, domain);

            data.add(fromUri(uri).path("err500").build());
            data.add(fromUri(uri).path("err_500").build());
        }

        return data;
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private URI uri;
    private String ncrndUri;

    public Weather500ConsistencyTest(URI uri) {
        this.uri = uri;
        this.mordaAllureBaseRule = new MordaAllureBaseRule()
                .withProxyAction(addHar("js-errors"));
        this.driver = mordaAllureBaseRule.getDriver();
        this.ncrndUri = uri.toString() + "?ncrnd=";
    }

    @Before
    public void setUp() throws InterruptedException {
        NavigationSteps.open(driver, uri);
        sleep(2000);
    }

    @Test
    public void noJSErrors() throws IOException {
        List<LogEntry> severeLogs = driver.manage().logs().get(LogType.BROWSER).getAll().stream()
                .filter(logEntry -> Level.SEVERE.equals(logEntry.getLevel()))
                .filter(e -> !e.getMessage().contains(uri.toString()))
                .collect(toList());

        assertThat("Detected " + severeLogs.size() + " js-errors: " + severeLogs, severeLogs, hasSize(0));
    }

    @Test
    public void statusCodeIs500() {
        Har har = mordaAllureBaseRule.getProxyServer().getHar();

        List<HarEntry> harEntries = har.getLog().getEntries().stream()
                .filter(e -> e.getRequest().getUrl().startsWith(uri.toString()))
                .filter(e -> e.getResponse().getStatus() >= 500)
                .collect(toList());

        assertThat("Должна быть хотя бы 1 500-ка на " + uri.toString(), harEntries, hasSize(greaterThan(0)));
        harEntries.forEach(e -> assertThat("Wrong response code on " + e.getRequest().getUrl(),
                e.getResponse().getStatus(), greaterThanOrEqualTo(500))

        );
    }

    @Test
    public void staticIsOk() {
        Har har = mordaAllureBaseRule.getProxyServer().getHar();
        har.getLog().getEntries()
                .removeIf(e -> e.getRequest().getUrl().equals(uri.toString()));
        har.getLog().getEntries()
                .removeIf(e -> e.getRequest().getUrl().startsWith(ncrndUri));
        har.getLog().getEntries()
                .removeIf(e -> e.getRequest().getUrl().contains("favicon.ico"));

        assertThat(uri.toString(), har, StaticDownloadedMatcher.staticDownloaded());
    }
}
