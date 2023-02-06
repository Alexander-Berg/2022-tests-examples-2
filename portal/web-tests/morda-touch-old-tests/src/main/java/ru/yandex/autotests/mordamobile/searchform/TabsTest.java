package ru.yandex.autotests.mordamobile.searchform;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.data.SearchData;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.Collection;

import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.mordamobile.data.SearchData.ALL_TABS;
import static ru.yandex.autotests.mordamobile.data.SearchData.REQUEST;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 12.12.13
 */
@Aqua.Test(title = "Табы")
@RunWith(Parameterized.class)
@Features("Search")
@Stories("Tabs")
public class TabsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(ALL_TABS);
    }

    private SearchData.TabInfo tabInfo;

    public TabsTest(SearchData.TabInfo tabInfo) {
        this.tabInfo = tabInfo;
    }

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void tabLink() {
        HtmlElement tab = user.findFirst(homePage.searchBlock.allTabs,
                on(HtmlElement.class), hasText(tabInfo.text));
        user.shouldSeeElement(tab);
        user.shouldSeeLink(tab, tabInfo);
    }

    @Test
    public void tabRequest() {
        user.shouldSeeElement(homePage.searchBlock.input);
        user.entersTextInInput(homePage.searchBlock.input, REQUEST);
        HtmlElement tab = user.findFirst(homePage.searchBlock.allTabs,
                on(HtmlElement.class), hasText(tabInfo.text));
        user.shouldSeeElement(tab);
        user.clicksOn(tab);
        user.shouldSeePage(tabInfo.request);
    }
}
