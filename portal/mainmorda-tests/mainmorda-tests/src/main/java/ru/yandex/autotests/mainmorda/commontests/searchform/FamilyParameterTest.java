package ru.yandex.autotests.mainmorda.commontests.searchform;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.SearchData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.pages.SerpPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.SearchData.FAMILY_PARAMETER_MATCHER;
import static ru.yandex.autotests.mainmorda.data.SearchData.FAMILY_SEARCH_URL;

/**
 * User: ivannik
 * Date: 21.06.13
 * Time: 12:57
 */
@Aqua.Test(title = "Проброс параметра family в серп при запросе")
@Features({"Main", "Common", "Search Form"})
@Stories("Family")
public class FamilyParameterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private SerpPage serpPage = new SerpPage(driver);

    @Before
    public void setUp() {
        user.initTest(FAMILY_SEARCH_URL, CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), FAMILY_SEARCH_URL, mordaAllureBaseRule);
    }

    @Test
    public void familyParameterThrown() {
        user.shouldSeeElement(mainPage.search.input);
        user.entersTextInInput(mainPage.search.input, SearchData.REQUEST_TEXT);
        user.clicksOn(mainPage.search.submit);
        user.shouldSeePage(FAMILY_PARAMETER_MATCHER);
        user.shouldSeeInputWithText(serpPage.search.input, equalTo(SearchData.REQUEST_TEXT));
    }
}
