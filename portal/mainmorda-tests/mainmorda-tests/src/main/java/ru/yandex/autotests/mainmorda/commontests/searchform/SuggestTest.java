package ru.yandex.autotests.mainmorda.commontests.searchform;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.SearchData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.pages.TuneSuggestPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

/**
 * User: eoff
 * Date: 11.12.12
 */
@Aqua.Test(title = "Пробрасывание запроса при поиске")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Search Form"})
@Stories("Suggest")
public class SuggestTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private TuneSuggestPage tuneSuggestPage = new TuneSuggestPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(SearchData.SUGGEST_TESTS);
    }

    private String request;

    public SuggestTest(String request) {
        this.request = request;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void suggestAppears() {
        user.shouldSeeElement(mainPage.search.input);
        user.clearsInput(mainPage.search.input);
        user.entersTextInInput(mainPage.search.input, request);
        user.shouldSeeElement(mainPage.search.suggest);
        user.clicksOn(mainPage.search.input);
        user.clearsInput(mainPage.search.input);
        user.entersTextInInput(mainPage.search.input, "");
        user.shouldNotSeeElement(mainPage.search.suggest);
    }

}
