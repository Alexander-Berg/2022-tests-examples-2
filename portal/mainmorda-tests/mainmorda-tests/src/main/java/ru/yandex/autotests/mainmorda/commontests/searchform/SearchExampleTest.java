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

import static org.hamcrest.Matchers.equalToIgnoringCase;
import static org.hamcrest.Matchers.not;

/**
 * User: eoff
 * Date: 10.12.12
 */
@Aqua.Test(title = "Пример запроса поиска")
@Features({"Main", "Common", "Search Form"})
@Stories("Example")
public class SearchExampleTest {
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
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void searchExampleText() {
        user.shouldSeeElement(mainPage.search.forExample);
        user.shouldSeeElementWithText(mainPage.search.forExample, SearchData.EXAMPLE_TEXT);
        user.shouldSeeElementWithText(mainPage.search.example, not(""));
        user.refreshPage();
        user.shouldSeeElementWithText(mainPage.search.example, not(""));
    }

    @Test
    public void searchExampleClick() {
        user.shouldSeeElement(mainPage.search.example);
        String example = mainPage.search.example.getText();
        user.clicksOn(mainPage.search.example);
        user.shouldSeePage(SearchData.SEARCH_URL);
        user.shouldSeeInputWithText(serpPage.search.input, equalToIgnoringCase(example));
    }

    @Test
    public void suggestDoesNotAppear() {
        user.clicksOn(mainPage.search.example);
        user.shouldNotSeeElement(mainPage.search.suggest);
    }
}
