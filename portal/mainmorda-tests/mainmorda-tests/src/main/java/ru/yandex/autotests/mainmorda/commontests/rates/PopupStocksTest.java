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
@Aqua.Test(title = "Котировки в попапе")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Rates"})
@Stories("Popup Rates Links")
public class PopupStocksTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private RatesSteps userRates = new RatesSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private int n;

    public PopupStocksTest(int n) {
        this.n = n;
    }

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        List<Integer> params = new ArrayList<>();
        for (int i = 0; i != RatesData.DEFAULT_RATES.size(); i++) {
            params.add(i);
        }
        return ParametrizationConverter.convert(params);
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void ratePopupLinks() {
        user.shouldSeeElement(mainPage.inlineRatesBlock);
        user.shouldSeeElement(mainPage.inlineRatesBlock.moreStocksButton);
        user.clicksOn(mainPage.inlineRatesBlock.moreStocksButton);
        user.shouldSeeElement(mainPage.ratesPopupBlock);
        user.shouldSeeListWithSize(mainPage.ratesPopupBlock.ratesLinks, greaterThan(n));
        userRates.shouldSeeDefaultRate(mainPage.ratesPopupBlock.ratesLinks, n);
        userRates.shouldSeeRatesLink(mainPage.ratesPopupBlock.ratesLinks, n, false);
    }

}
