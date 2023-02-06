package ru.yandex.autotests.morda.tests.web.common.search;

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

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 09.12.2015.
 */
@Aqua.Test(title = "Отсутствие элементов с BADID")
@Features("Search")
@Stories("Отсутствие элементов с BADID")
@RunWith(Parameterized.class)
public class BadIdInCounterTest {
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
    private DesktopMainPage page;

    public BadIdInCounterTest(Morda<DesktopMainPage> morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);

    }

    @Before
    public void init() {
        morda.initialize(driver);
        driver.manage().deleteCookieNamed("yandexuid");
        driver.manage().addCookie(new Cookie("yandexuid", "7086015271313068940"));
        user.refreshPage();
    }

    @Test
    public void badIdInCounterTest() {
        user.shouldSeeListWithSize(page.elementsWithBadId, equalTo(0));
    }
}
