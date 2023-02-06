package ru.yandex.autotests.mainmorda.commontests.searchtabs;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TabsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TabSteps;
import ru.yandex.autotests.mainmorda.utils.TabInfo;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.TabsData.SIZE_EXTRA_SMALL;

/**
 * User: eoff
 * Date: 03.12.12
 */
@Aqua.Test(title = "Ссылки табов 'еще'")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Search Tabs"})
@Stories("More")
public class MoreTabsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TabSteps userTab = new TabSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(TabsData.MORE_TABS);
    }

    private TabInfo tab;

    public MoreTabsTest(TabInfo tab) {
        this.tab = tab;
    }

    @Before
    public void setUp() {
        user.resizeWindow(SIZE_EXTRA_SMALL);
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void tabLink() throws Exception {
        user.clicksOn(mainPage.search.more);
        userTab.shouldSeeTab(mainPage.search.allMoreTabs, tab);
    }
}
