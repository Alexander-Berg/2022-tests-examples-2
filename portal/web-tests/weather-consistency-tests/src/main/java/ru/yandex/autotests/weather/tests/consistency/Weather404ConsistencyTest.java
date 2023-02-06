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

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static java.lang.Thread.sleep;
import static java.net.HttpURLConnection.HTTP_NOT_FOUND;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.collection.IsCollectionWithSize.hasSize;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

/**
 * User: asamar
 * Date: 26.01.17
 */
@Aqua.Test(title = "404 consistency")
@RunWith(Parameterized.class)
@Features("Consistency")
public class Weather404ConsistencyTest {
    private static final WeatherWebTestsProperties CONFIG = new WeatherWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<URI> data() {
        List<URI> data = new ArrayList<>();

        String scheme = CONFIG.getWeatherScheme();
        String environment = CONFIG.getWeatherEnvironment();

        for (String domain : asList(".ru", ".ua", ".kz", ".by")) {

            URI uri = fromUri("{scheme}://{env}.yandex{domain}/pogoda/")
                    .build(scheme, environment, domain);

            data.add(fromUri(uri).path("sl/blah").build());
        }

        data.add(fromUri("{scheme}://{env}.yandex.com.tr/hava/sl/blah")
                .build(scheme, environment));

        return data;
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private URI uri;
    private String ncrndUri;

    public Weather404ConsistencyTest(URI uri) {
        this.uri = uri;
        this.mordaAllureBaseRule = new MordaAllureBaseRule()
                .withProxyAction(addHar("js-errors"));
        this.driver = mordaAllureBaseRule.getDriver();
        ncrndUri = uri.toString() + "?ncrnd=";
    }

    @Before
    public void setUp() throws InterruptedException {
        NavigationSteps.open(driver, uri);
        sleep(2000);
    }

    @Test
    public void noJSErrors() throws IOException {
        List<LogEntry> severeLogs = select(driver.manage().logs().get(LogType.BROWSER).getAll(),
                having(on(LogEntry.class).getLevel(), equalTo(Level.SEVERE)));

        List<LogEntry> severeLogs1 = severeLogs.stream()
                .filter(e -> !e.getMessage().contains(uri.toString()))
        .collect(toList());

        assertThat("Detected " + severeLogs1.size() + " js-errors: " + severeLogs1, severeLogs1, hasSize(0));
    }

    @Test
    public void statusCodeIs404() {
        Har har = mordaAllureBaseRule.getProxyServer().getHar();

        List<HarEntry> harEntries = har.getLog().getEntries().stream()
                .filter(e -> e.getRequest().getUrl().startsWith(uri.toString()))
                .filter(e -> e.getResponse().getStatus() == HTTP_NOT_FOUND)
                .collect(toList());

        assertThat("Должна быть хотя бы 1 404-я на " + uri.toString(), harEntries, hasSize(greaterThan(0)));
        harEntries.forEach(e -> assertThat("Wrong response code on " + e.getRequest().getUrl(),
                e.getResponse().getStatus(), equalTo(HTTP_NOT_FOUND)));
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
