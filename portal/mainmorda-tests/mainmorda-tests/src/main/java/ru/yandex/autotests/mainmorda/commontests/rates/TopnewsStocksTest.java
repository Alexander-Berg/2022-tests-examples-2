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
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assume.assumeThat;

/**
 * User: eoff
 * Date: 05.02.13
 */
@Aqua.Test(title = "Дефолтные котировки в новостях")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Rates"})
@Stories("Default News Rates")
public class TopnewsStocksTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private RatesSteps userRates = new RatesSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private int n;

    public TopnewsStocksTest(int n) {
        this.n = n;
    }

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        List<Integer> params = new ArrayList<>();
        for (int i = 0; i != RatesData.DEFAULT_INLINE_RATES.size(); i++) {
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
    public void rateInlineLinksLink() {
        user.shouldSeeElement(mainPage.inlineRatesBlock);
        user.shouldSeeListWithSize(mainPage.inlineRatesBlock.ratesLinks, greaterThan(n));
        userRates.shouldSeeDefaultInlineRate(mainPage.inlineRatesBlock.ratesLinks, n);
        userRates.shouldSeeRatesLink(mainPage.inlineRatesBlock.ratesLinks, n, true);
    }

}
