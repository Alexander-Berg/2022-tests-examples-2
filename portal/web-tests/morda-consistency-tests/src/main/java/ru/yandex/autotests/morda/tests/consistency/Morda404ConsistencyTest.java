package ru.yandex.autotests.morda.tests.consistency;

import net.lightbody.bmp.core.har.Har;
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
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.matchers.StaticDownloadedMatcher;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Level;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static java.lang.Thread.sleep;
import static java.net.HttpURLConnection.HTTP_NOT_FOUND;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404by;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404com;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404comTr;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404kz;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404ru;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404ua;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

/**
 * User: alex89
 * Date: 18.03.13
 */

@Aqua.Test(title = "Проверка отсутствия js-ошибок 404")
@RunWith(Parameterized.class)
@Features("Consistency")
public class Morda404ConsistencyTest {
    private static final Logger LOG = Logger.getLogger(Morda404ConsistencyTest.class);
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<?>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.add(desktop404ru(scheme, environment));
        data.add(desktop404ua(scheme, environment));
        data.add(desktop404kz(scheme, environment));
        data.add(desktop404by(scheme, environment));
        data.add(desktop404comTr(scheme, environment));
        data.add(desktop404com(scheme, environment));
        return ParametrizationConverter.convert(data);
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private Morda<?> morda;

    public Morda404ConsistencyTest(Morda<?> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule()
                .withProxyAction(addHar("js-errors"));
        this.driver = mordaAllureBaseRule.getDriver();
    }

    @Before
    public void setUp() throws InterruptedException {
        morda.initialize(driver);
        sleep(2000);
    }

    @Test
    public void noJSErrors() throws IOException {
        List<LogEntry> severeLogs = select(driver.manage().logs().get(LogType.BROWSER).getAll(),
                having(on(LogEntry.class).getLevel(), equalTo(Level.SEVERE)));

        severeLogs.removeIf(e ->
                e.getMessage().contains(morda.getUrl().toString()) &&
                e.getMessage().contains("404"));

        assertThat("Detected " + severeLogs.size() + " js-errors: " + severeLogs, severeLogs, hasSize(0));
    }

    @Test
    public void statusCodeIs404() {
        Har har = mordaAllureBaseRule.getProxyServer().getHar();
        har.getLog().getEntries().stream()
                .filter(e -> e.getRequest().getUrl().equals(morda.getUrl().toString()))
                .forEach(e -> assertThat("Wrong response code", e.getResponse().getStatus(), equalTo(HTTP_NOT_FOUND)));
    }

    @Test
    public void staticIsOk() {
        Har har = mordaAllureBaseRule.getProxyServer().getHar();
        har.getLog().getEntries().removeIf(e -> e.getRequest().getUrl().equals(morda.getUrl().toString()));

        assertThat(morda.toString(), har, StaticDownloadedMatcher.staticDownloaded());
    }
}

