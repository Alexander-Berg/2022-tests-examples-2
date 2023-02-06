package ru.yandex.autotests.mordacom.tabs;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacom.steps.YandexUidSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.data.TabsData;
import ru.yandex.autotests.mordacom.steps.SearchSteps;
import ru.yandex.autotests.mordacom.utils.TabInfo;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacom.data.TabsData.getAllTabs;
import static ru.yandex.autotests.utils.morda.auth.User.COM_DEFAULT;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@Aqua.Test(title = "Табы и проброс запросов в залогиненном режиме")
@RunWith(Parameterized.class)
@Features("Search Tabs")
@Stories("Tabs Login")
public class TabsLoginTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SearchSteps userSearch = new SearchSteps(driver);
    private YandexUidSteps userUid = new YandexUidSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Language language : CONFIG.getMordaComLangs()) {
            for (TabInfo tab : getAllTabs(language)) {
                data.add(new Object[]{language, tab});
            }
        }
        return data;
    }

    private final Language language;
    private final TabInfo tab;

    public TabsLoginTest(Language language, TabInfo tab) {
        this.language = language;
        this.tab = tab;
    }

    @Before
    public void setUp() throws InterruptedException {
        user.logsInAs(COM_DEFAULT, CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.search);
    }

    @Test
    public void tabLinkLogon() {
        userSearch.shouldSeeNewTab(homePage.tabsBlock.tabs, tab);
    }

    @Test
    public void requestCorrectlyThrownLogon() {
        userSearch.shouldSeeTabRequestCorrectlyThrown(homePage.tabsBlock.tabs, tab);
    }

    @Test
    public void requestCorrectlyThrownLogonWithCounters() {
        userUid.setsUIDWithCounters();
        user.refreshPage();
        userSearch.shouldSeeTabRequestCorrectlyThrown(homePage.tabsBlock.tabs, tab);
    }
}
