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
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 25.12.12
 */
@Aqua.Test(title = "Настройки Котировок")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Rates")
public class RatesSettingsTest {
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
    public void checkDefaultSettings() {
        user.shouldSeeSelectWithSize(mainPage.ratesSettings.selectRatesToRemove,
                equalTo(RatesSettingsData.DEFAULT_LIST_SIZE));
        user.shouldSeeElementIsSelected(mainPage.ratesSettings.autoReloadCheckbox);
        user.shouldSeeElementIsSelected(mainPage.ratesSettings.highlightCheckbox);
    }

    @Test
    public void checkBoxSave() {
        user.selectElement(mainPage.ratesSettings.highlightCheckbox);
        user.clicksOn(mainPage.ratesSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.clicksOn(mainPage.ratesBlock.editIcon);
        user.shouldSeeElementIsSelected(mainPage.ratesSettings.highlightCheckbox);
        user.deselectElement(mainPage.ratesSettings.highlightCheckbox);
        user.clicksOn(mainPage.ratesSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.ratesBlock);
        user.shouldSeeElement(mainPage.ratesBlock.editIcon);
        user.clicksOn(mainPage.ratesBlock.editIcon);
        user.shouldSeeElementIsNotSelected(mainPage.ratesSettings.highlightCheckbox);
    }

    @Test
    public void selectAllButtons() {
        int beforeNew = mainPage.ratesSettings.selectRatesToAdd.getOptions().size();
        int beforeOld = mainPage.ratesSettings.selectRatesToRemove.getOptions().size();
        user.clicksOn(mainPage.ratesSettings.addAllRatesButton);
        user.shouldSeeSelectWithSize(mainPage.ratesSettings.selectRatesToRemove,
                equalTo(beforeNew + beforeOld));
        user.shouldSeeSelectWithSize(mainPage.ratesSettings.selectRatesToAdd,
                equalTo(0));
        user.clicksOn(mainPage.ratesSettings.removeAllRatesButton);
        user.shouldSeeSelectWithSize(mainPage.ratesSettings.selectRatesToRemove,
                equalTo(1));
        user.shouldSeeSelectWithSize(mainPage.ratesSettings.selectRatesToAdd,
                equalTo(beforeNew + beforeOld - 1));
    }

    @Test
    public void addRate() {
        String rate = userRates.selectRandomRate();
        user.clicksOn(mainPage.ratesSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userMode.saveSettings();
        userRates.shouldSeeRate(rate);
    }
}
