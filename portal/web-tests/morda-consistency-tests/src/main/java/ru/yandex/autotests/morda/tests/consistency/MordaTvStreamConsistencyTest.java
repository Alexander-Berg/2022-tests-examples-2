package ru.yandex.autotests.morda.tests.consistency;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
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
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.matchers.StaticDownloadedMatcher;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.language.Language;
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
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda.touchRu;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: alex89
 * Date: 18.03.13
 */

@Aqua.Test(title = "Проверка отсутствия js-ошибок TvStream")
@RunWith(Parameterized.class)
@Features("Consistency")
public class MordaTvStreamConsistencyTest {
    public static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final Logger LOG = Logger.getLogger(MordaTvStreamConsistencyTest.class);
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private Morda<?> morda;
    private URI url;

    public MordaTvStreamConsistencyTest(Morda<?> morda, URI url) {
        this.morda = morda;
        this.url = url;
        this.mordaAllureBaseRule = this.morda.getRule()
                .withProxyAction(addHar("js-errors"));
        this.driver = mordaAllureBaseRule.getDriver();
    }

    @Parameterized.Parameters(name = "{0},{1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();

        List<Morda<?>> mordas = asList(
                desktopMain(scheme, environment, MOSCOW),
                touchRu(scheme, environment, userAgentTouchIphone, MOSCOW, Language.RU)
        );

        List<String> channels = asList("100000", "743");

        for (Morda<?> morda : mordas) {
            URI mordaUrl = morda.getUrl();
            
            data.add(new Object[]{morda, UriBuilder.fromUri(mordaUrl).path("portal/video").build()});
            data.add(new Object[]{morda, UriBuilder.fromUri(mordaUrl).path("portal/tvstream").build()});
            for (String channel : channels) {
                data.add(new Object[]{morda, UriBuilder.fromUri(mordaUrl).path("efir").queryParam("stream_channel", channel).build()});
            }
        }

        return data;
    }

    @Before
    public void setUp() throws InterruptedException {
        morda.initialize(driver);
        NavigationSteps.open(driver, url);
        sleep(5000);
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
    public void staticIsOk() throws JsonProcessingException {
        assertThat(morda.toString(), mordaAllureBaseRule.getProxyServer().getHar(),
                StaticDownloadedMatcher.staticDownloaded());
    }
}

