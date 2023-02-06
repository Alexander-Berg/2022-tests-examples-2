package ru.yandex.autotests.mainmorda.commontests.rates;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.RatesData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.RatesSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.greaterThan;

/**
 * User: eoff
 * Date: 05.02.13
 */
@Aqua.Test(title = "Вид попапа котировок")
@Features({"Main", "Common", "Rates"})
@Stories("Popup Rates Appearance")
public class PopupStocksAppearanceTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private RatesSteps userRates = new RatesSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void ratePopup() {
        user.shouldSeeElement(mainPage.inlineRatesBlock);
        user.shouldSeeElement(mainPage.inlineRatesBlock.moreStocksButton);
        user.clicksOn(mainPage.inlineRatesBlock.moreStocksButton);

        user.shouldSeeElement(mainPage.ratesPopupBlock);
        user.shouldSeeListWithSize(mainPage.ratesPopupBlock.ratesLinks, greaterThan(0));

        user.shouldSeeElement(mainPage.ratesPopupBlock.close);
        user.clicksOn(mainPage.ratesPopupBlock.close);
        user.shouldNotSeeElement(mainPage.ratesPopupBlock);
    }

}
