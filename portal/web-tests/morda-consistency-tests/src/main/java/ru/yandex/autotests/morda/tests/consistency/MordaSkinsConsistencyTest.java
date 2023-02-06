package ru.yandex.autotests.morda.tests.consistency;

import org.apache.log4j.Logger;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;
import static org.openqa.selenium.remote.DesiredCapabilities.chrome;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: alex89
 * Date: 18.03.13
 */

@Aqua.Test(title = "Проверка наличия данных для скинов")
@RunWith(Parameterized.class)
@Features("Consistency")
public class MordaSkinsConsistencyTest {
    private static final Logger LOG = Logger.getLogger(MordaSkinsConsistencyTest.class);
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<URI> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        URI mainMordaUrl = desktopMain(scheme, environment, MOSCOW).getUrl();

        data.add(fromUri(mainMordaUrl).path("themes/doom").build());

        return ParametrizationConverter.convert(data);
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private URI uri;

    public MordaSkinsConsistencyTest(URI uri) {
        this.uri = uri;
        this.mordaAllureBaseRule = new MordaAllureBaseRule();
        this.driver = mordaAllureBaseRule.getDriver();
    }

    @Before
    public void setUp() throws InterruptedException {
        NavigationSteps.open(driver, uri);
    }

    @Test
    public void hasSkinUrl() throws IOException {
        boolean doomUrl = (Boolean) ((JavascriptExecutor)driver).executeScript("return window.doomUrls !== undefined;");
        assertThat("No skin data found for doom", doomUrl, is(true));
    }
}

