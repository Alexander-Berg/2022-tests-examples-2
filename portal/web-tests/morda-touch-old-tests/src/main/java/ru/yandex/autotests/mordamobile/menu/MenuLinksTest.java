package ru.yandex.autotests.mordamobile.menu;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.data.MenuData;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.steps.MenuSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mordamobile.data.MenuData.TabInfo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.05.13
 */
@Aqua.Test(title = "Ссылки выпадающего меню")
@RunWith(Parameterized.class)
@Features("Menu")
@Stories("Links")
public class MenuLinksTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private MenuSteps userMenu = new MenuSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(MenuData.ALL_LINKS);
    }

    private TabInfo tab;

    public MenuLinksTest(TabInfo tab) {
        this.tab = tab;
    }

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.menuButton);
        Thread.sleep(2000);
        user.clicksOn(homePage.menuButton);
        user.shouldSeeElement(homePage.menuBlock);
        Thread.sleep(2000);
    }

    @Test
    public void menuLink() {
        userMenu.shouldSeeMenuLink(homePage.menuBlock.allTabs, tab);
    }
}
