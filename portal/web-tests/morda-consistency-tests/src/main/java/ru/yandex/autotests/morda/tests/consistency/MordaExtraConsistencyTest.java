package ru.yandex.autotests.morda.tests.consistency;

import org.apache.log4j.Logger;
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
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.matchers.StaticDownloadedMatcher;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Level;
import java.util.stream.Collectors;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.openqa.selenium.remote.DesiredCapabilities.chrome;
import static ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda.desktopHwLgV2;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: alex89
 * Date: 18.03.13
 */

@Aqua.Test(title = "Проверка отсутствия js-ошибок URLS")
@RunWith(Parameterized.class)
@Features("Consistency")
public class MordaExtraConsistencyTest {
    private static final Logger LOG = Logger.getLogger(MordaExtraConsistencyTest.class);
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<URI> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        URI mainMordaUrl = desktopMain(scheme, environment, MOSCOW).getUrl();
        URI hwLgV2Url = desktopHwLgV2(scheme, environment).getUrl();

        data.add(fromUri(hwLgV2Url).path("cityselect.html").queryParam("page", "index.html").build());
        data.add(fromUri(mainMordaUrl).path("data/samsung/combined.xml").build());
        data.add(fromUri(mainMordaUrl).path("themes").build());
        data.add(fromUri(mainMordaUrl).queryParam("edit", "1").build());
        data.add(fromUri(mainMordaUrl)
                .queryParam("content", "tv")
                .build());
        data.add(fromUri(mainMordaUrl)
                .queryParam("content", "chromenewtab")
                .build());
        data.add(fromUri(mainMordaUrl)
                .queryParam("cover", "johnlennon")
                .build());
        data.add(fromUri(mainMordaUrl)
                .queryParam("cover", "gagarin")
                .build());
        data.add(fromUri(mainMordaUrl)
                .queryParam("gramps", "1")
                .build());
        data.add(fromUri(mainMordaUrl)
                .path("portal/tvstream")
                .queryParam("content", "touch")
                .build());
        data.add(fromUri(mainMordaUrl)
                .path("portal/tvstream")
                .build());
        data.add(fromUri(mainMordaUrl)
                .path("portal/video")
                .build());        
        
        return ParametrizationConverter.convert(data);
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private URI uri;

    public MordaExtraConsistencyTest(URI uri) {
        this.uri = uri;
        this.mordaAllureBaseRule = new MordaAllureBaseRule()
                .withProxyAction(addHar("js-errors"));
        this.driver = mordaAllureBaseRule.getDriver();
    }

    @Before
    public void setUp() throws InterruptedException {
        NavigationSteps.open(driver, uri);
    }

    @Test
    public void noJSErrors() throws IOException {
        List<LogEntry> severeLogs = driver.manage().logs().get(LogType.BROWSER).getAll().stream()
                .filter(e -> !e.getMessage().contains("NS_ERROR_ILLEGAL_VALUE")
                        && !e.getMessage().contains("NS_ERROR_FAILURE")
                        && e.getLevel().equals(Level.SEVERE))
                .collect(Collectors.toList());

        assertThat("Detected " + severeLogs.size() + " js-errors: " + severeLogs, severeLogs, hasSize(0));
    }

    @Test
    public void staticIsOk() {
        assertThat(uri.toString(), mordaAllureBaseRule.getProxyServer().getHar(),
                StaticDownloadedMatcher.staticDownloaded());
    }
}

