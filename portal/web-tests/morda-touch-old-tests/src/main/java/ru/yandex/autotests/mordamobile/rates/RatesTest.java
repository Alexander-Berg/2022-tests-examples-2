package ru.yandex.autotests.mordamobile.rates;

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

import static ru.yandex.autotests.mordamobile.data.RatesData.RATES_TITLE;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.05.13
 */
@Aqua.Test(title = "Блок котировок")
@Features("Rates")
public class RatesTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.ratesBlock);
    }

    @Test
    public void ratesTitle() {
        user.shouldSeeElement(homePage.ratesBlock.title);
        user.shouldSeeElementWithText(homePage.ratesBlock.title, RATES_TITLE);
    }
}
