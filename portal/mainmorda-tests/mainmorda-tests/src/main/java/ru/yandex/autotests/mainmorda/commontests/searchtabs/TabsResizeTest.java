package ru.yandex.autotests.mainmorda.commontests.searchtabs;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TabsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TabSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mainmorda.data.TabsData.MAIN_TABS_EXTRA_SMALL;
import static ru.yandex.autotests.mainmorda.data.TabsData.SIZE_AVG;
import static ru.yandex.autotests.mainmorda.data.TabsData.SIZE_BIG;
import static ru.yandex.autotests.mainmorda.data.TabsData.SIZE_EXTRA_SMALL;
import static ru.yandex.autotests.mainmorda.data.TabsData.SIZE_SMALL;

/**
 * User: eoff
 * Date: 07.12.12
 */
@Aqua.Test(title = "Адаптивность табов")
@Features({"Main", "Common", "Search Tabs"})
@Stories("Adaptive Tabs")
public class TabsResizeTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TabSteps userTab = new TabSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void extraminTabsCount() {
        user.resizeWindow(SIZE_EXTRA_SMALL);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.tabsHidden),
                MAIN_TABS_EXTRA_SMALL);
        user.clicksOn(mainPage.search.more);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.moreTabsHidden),
                TabsData.MORE_TABS_EXTRA_SMALL);
    }

    @Test
    public void minTabsCount() {
//        assumeTrue(!CONFIG.getLang().equals(Language.KK) && !CONFIG.getLang().equals(Language.TT));
        user.resizeWindow(SIZE_SMALL);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.tabsHidden),
                TabsData.MAIN_TABS_SMALL);
        user.clicksOn(mainPage.search.more);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.moreTabsHidden),
                TabsData.MORE_TABS_SMALL);
    }


    @Test
    public void avgTabsCount() {
        assumeTrue(!CONFIG.getLang().equals(Language.KK) && !CONFIG.getLang().equals(Language.TT));
        user.resizeWindow(SIZE_AVG);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.tabsHidden),
                TabsData.MAIN_TABS_AVG);
        user.clicksOn(mainPage.search.more);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.moreTabsHidden),
                TabsData.MORE_TABS_AVG);
    }

    @Test
    public void maxTabsCount() {
        user.resizeWindow(SIZE_BIG);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.tabsHidden),
                TabsData.MAIN_TABS_FULL);
        user.clicksOn(mainPage.search.more);
        userTab.canSeeAllTabsRequired(userTab.getVisibleElements(mainPage.search.moreTabsHidden),
                TabsData.MORE_TABS_FULL);
    }
}
