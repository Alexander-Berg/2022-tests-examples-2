package ru.yandex.autotests.mordamobile.menu;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordamobile.data.MenuData.ALL_LINKS;
import static ru.yandex.autotests.mordamobile.data.MenuData.TITLE_TEXT;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25.04.13
 */

@Aqua.Test(title = "Выпадающее меню")
@Features("Menu")
@Stories("Appearance")
public class MenuTest {

    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule(DesiredCapabilities.chrome());

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.menuButton);
        Thread.sleep(2000);
        user.clicksOn(homePage.menuButton);
        user.shouldSeeElement(homePage.menuBlock);
    }

    @Test
    public void menuCloses() {
        user.shouldSeeElement(homePage.menuButton);
        user.clicksOn(homePage.menuButton);
        user.shouldNotSeeElement(homePage.menuBlock);
    }

    @Test
    public void menuTitle() {
        user.shouldSeeElement(homePage.menuBlock.title);
        user.shouldSeeElementWithText(homePage.menuBlock.title, TITLE_TEXT);
    }

    @Test
    public void menuSize() {
        user.shouldSeeListWithSize(homePage.menuBlock.allTabs, equalTo(ALL_LINKS.size()));
    }
}
