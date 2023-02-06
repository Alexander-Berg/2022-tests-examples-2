package ru.yandex.autotests.turkey.seachtabs;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.data.TabsData;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.SearchSteps;
import ru.yandex.autotests.turkey.utils.TabInfo;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.turkey.data.SearchData.FAMILY_SEARCH_URL;

/**
 * User: ivannik
 * Date: 24.06.13
 * Time: 17:09
 */
@Aqua.Test(title = "Проброс параметра family в табы при запросе")
@RunWith(Parameterized.class)
@Features("Search Tabs")
@Stories("Tabs Family")
public class FamilyParameterTabsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();

    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SearchSteps userSearch = new SearchSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(TabsData.ALL_TABS);
    }

    private TabInfo tab;

    public FamilyParameterTabsTest(TabInfo tab) {
        this.tab = tab;
    }

    @Before
    public void setUp() {
        user.opensPage(FAMILY_SEARCH_URL);
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.shouldSeeElement(yandexComTrPage.search);
    }

    @Test
    public void familyParameterThrown() {
        userSearch.shouldSeeFamilyParameterThrown(yandexComTrPage.tabsBlock.tabs, tab);
    }
}
