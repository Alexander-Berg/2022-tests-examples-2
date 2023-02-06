package ru.yandex.autotests.mordamobile.searchform;

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
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordamobile.data.SearchData.SEARCH_URL;
import static ru.yandex.autotests.mordamobile.data.SearchData.TEXT;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Пробрасывание запроса")
@Features("Search")
@Stories("Request")
public class RequestTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void requestThrown() {
        user.shouldSeeElement(homePage.searchBlock.input);
        user.entersTextInInput(homePage.searchBlock.input, TEXT);
        user.shouldSeeElement(homePage.searchBlock.searchButton);
        user.clicksOn(homePage.searchBlock.searchButton);
        user.shouldSeePage(SEARCH_URL);
    }
}
