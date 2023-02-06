package ru.yandex.autotests.morda.tests.web.common.resources;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 10.12.2015.
 */
@Aqua.Test(title = "Имя сервера")
@Features("Resources")
@Stories("Server Name")
@RunWith(Parameterized.class)
public class ServerNameTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<DesktopMainPage> morda;
    public Matcher<String> MACHINE_NAME_MATCHER;

    public ServerNameTest(Morda<DesktopMainPage> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);

    }

    @Before
    public void init() {
        morda.initialize(driver);
        driver.manage().deleteCookieNamed("yandexuid");
        driver.manage().addCookie(new Cookie("yandexuid", "7086015271313068940"));
        user.refreshPage();

        if( morda.getEnvironment().getEnvironment().contains("rc")){
            MACHINE_NAME_MATCHER = matches("<!--wrc-(m|u|n|e|i|s|a|v)[\\d]+\\.yandex\\.net-->");
        } else {
            MACHINE_NAME_MATCHER = matches("<!--(w-dev[\\d]*|v\\d+\\.wdevx)\\.yandex\\.net-->");
        }
    }

    @Test
    public void serverNameTest() {
        String html = driver.getPageSource();
        assertThat(html, containsString(".yandex.net-->"));
        String name = html.substring(0, html.indexOf(".yandex.net-->") + ".yandex.net-->".length());
        name = name.substring(name.lastIndexOf("<!--"));
        assertThat(name, MACHINE_NAME_MATCHER);
    }
}
