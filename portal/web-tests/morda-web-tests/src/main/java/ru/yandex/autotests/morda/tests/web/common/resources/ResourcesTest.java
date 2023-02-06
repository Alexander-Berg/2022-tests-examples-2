package ru.yandex.autotests.morda.tests.web.common.resources;

import jdk.nashorn.internal.ir.annotations.Ignore;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
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

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.lessThan;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 10.12.2015.
 */
@Aqua.Test(title = "Ресурсы с dev-машин")
@Features("Resources")
@Stories("Ресурсы с dev-машин")
@RunWith(Parameterized.class)
public class ResourcesTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<DesktopMainPage> morda;
    private CommonMordaSteps user;

    public ResourcesTest(Morda<DesktopMainPage> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
    }

    @Before
    public void init() {
        assumeFalse("Need not dev", !morda.getEnvironment().getEnvironment().contains("rc"));
        morda.initialize(driver);
    }

    @Test
    public void resourcesTest() {
        String html = driver.getPageSource();
        assertThat(html, not(anyOf(
                        containsString("cloudkill"),
                        containsString("graymantle"),
                        containsString("wdevx")))
        );
    }

    @Test
    @Ignore
    public void mordaSize() throws MalformedURLException {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, WIDGET), morda.getPassportUrl().toURL());
//        modeSteps.setModeLogged(PLAIN);
        int plainSize = driver.getPageSource().length();
//        modeSteps.setModeLogged(WIDGET);
        int widgetSize = driver.getPageSource().length();
        assertThat(1.0 * widgetSize / plainSize, lessThan(2.0));
    }
}
