package ru.yandex.autotests.mordamobile.apps;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordamobile.data.AppsData.ALL_APPS_LINK;
import static ru.yandex.autotests.mordamobile.data.AppsData.TITLE_LINK;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок мобильных приложений")
@Features("Apps")
public class AppsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.appsBlock);
    }

    @Test
    public void appsTitle() {
        user.shouldSeeLink(homePage.appsBlock.title, TITLE_LINK);
    }

    @Test
    public void allAppsLink() {
        user.shouldSeeLink(homePage.appsBlock.allApps, ALL_APPS_LINK);
    }

    @Test
    public void appsSize() {
        user.shouldSeeListWithSize(homePage.appsBlock.apps, equalTo(4));
    }
}
