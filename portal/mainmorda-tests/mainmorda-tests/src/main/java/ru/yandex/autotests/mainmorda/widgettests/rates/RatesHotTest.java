package ru.yandex.autotests.mainmorda.widgettests.rates;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.RatesSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: eoff
 * Date: 05.02.13
 */
@Aqua.Test(title = "Горячие котировки")
@Features({"Main", "Widget", "Rates Block"})
@Stories("Hot")
public class RatesHotTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private RatesSteps userRates = new RatesSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userWidget.addWidget("_stocks");
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.ratesBlock);
        user.moveMouseOn(mainPage.ratesBlock);
        user.clicksOn(mainPage.ratesBlock.editIcon);
        user.shouldSeeElement(mainPage.ratesSettings);
        user.clicksOn(mainPage.ratesSettings.addAllRatesButton);
        user.clicksOn(mainPage.ratesSettings.okButton);
        user.shouldNotSeeElement(mainPage.ratesSettings);
        user.shouldSeeElement(mainPage.widgetSettingsHeader);
        userMode.saveSettings();
    }

    @Test
    public void hotRatesOff() {
        user.shouldSeeElement(mainPage.ratesBlock);
        List<String> hotRates = userRates.getHotRatesTexts();
        userRates.turnOffHighLightning();
        List<String> newHotRates = userRates.getHotRatesTexts();
        user.shouldSeeListWithSize(newHotRates, equalTo(0));
        userRates.turnOnHighLightning();
        userRates.shouldSeeHotRates(hotRates);
    }
}
