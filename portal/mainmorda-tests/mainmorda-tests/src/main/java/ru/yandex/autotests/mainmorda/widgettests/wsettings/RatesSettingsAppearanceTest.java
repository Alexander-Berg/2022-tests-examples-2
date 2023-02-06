package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.RatesSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.RatesSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 25.12.12
 */
@Aqua.Test(title = "Внешний вид настроек котировок")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Rates")
public class RatesSettingsAppearanceTest {
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
        user.clicksOn(mainPage.ratesBlock.editIcon);
        user.shouldSeeElement(mainPage.ratesSettings);
    }

    @Test
    public void buttonsTexts() {
        user.shouldSeeElementMatchingTo(mainPage.ratesSettings.addAllRatesButton,
                hasAttribute(HtmlAttribute.VALUE, RatesSettingsData.ADD_ALL_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.ratesSettings.addOneRateButton,
                hasAttribute(HtmlAttribute.VALUE, RatesSettingsData.ADD_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.ratesSettings.removeAllRatesButton,
                hasAttribute(HtmlAttribute.VALUE, RatesSettingsData.REMOVE_ALL_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.ratesSettings.removeOneRateButton,
                hasAttribute(HtmlAttribute.VALUE, RatesSettingsData.REMOVE_TEXT));
    }

    @Test
    public void ratesTitle() {
        user.shouldSeeElement(mainPage.ratesSettings.ratesTitle);
        userRates.shouldSeeRatesTitle(RatesSettingsData.RATES_TITLE);
    }

    @Test
    public void highLightCheckBox() {
        user.shouldSeeElement(mainPage.ratesSettings.highlightCheckbox);
        user.shouldSeeElementWithText(mainPage.ratesSettings.highlightCheckbox,
                RatesSettingsData.RATES_HIGHLIGHT);
    }
}
