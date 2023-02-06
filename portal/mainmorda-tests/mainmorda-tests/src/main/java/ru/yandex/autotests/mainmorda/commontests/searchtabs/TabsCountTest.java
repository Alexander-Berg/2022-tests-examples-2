package ru.yandex.autotests.mainmorda.commontests.searchtabs;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.TabsData.MAIN_TABS_DEFAULT;
import static ru.yandex.autotests.mainmorda.data.TabsData.MORE_TABS_DEFAULT;
import static ru.yandex.autotests.mainmorda.data.TabsData.SIZE_BIG;
import static ru.yandex.autotests.mainmorda.data.TabsData.TABS_HIDDEN;


/**
 * User: eoff
 * Date: 07.12.12
 */
@Aqua.Test(title = "Количество табов")
@Features({"Main", "Common", "Search Tabs"})
@Stories("Count")
public class TabsCountTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.resizeWindow(SIZE_BIG);
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void tabsNumber() {
        user.shouldSeeListWithSize(mainPage.search.tabs, equalTo(MAIN_TABS_DEFAULT.size()));
        user.shouldSeeListWithSize(mainPage.search.tabsHidden, equalTo(TABS_HIDDEN.size()));
    }

    @Test
    public void moreTabsNumber() {
        user.clicksOn(mainPage.search.more);
        user.shouldSeeListWithSize(mainPage.search.moreTabs, equalTo(MORE_TABS_DEFAULT.size()));
        user.shouldSeeListWithSize(mainPage.search.moreTabsHidden, equalTo(TABS_HIDDEN.size()));
    }
}
