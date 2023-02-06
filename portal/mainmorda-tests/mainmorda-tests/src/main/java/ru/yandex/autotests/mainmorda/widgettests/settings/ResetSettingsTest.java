package ru.yandex.autotests.mainmorda.widgettests.settings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.WidgetsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.InformationsMessages.RESET_INFO_MESSAGE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: alex89
 * Date: 11.01.13
 */

@Aqua.Test(title = "Сброс настроек")
@Features({"Main", "Widget", "Settings"})
@Stories("Reset Settings")
public class ResetSettingsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void resetSettingsAfterPlainMode() {
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.widgetSettingsHeader.resetButton);
        userWidget.clickOnResetButtonAndAcceptsAlert();
        userMode.shouldSeePlainMode();
    }

    @Test
    public void resetSettingsAfterSaving() {
        userMode.setWidgetMode(CONFIG.getBaseURL());
        userMode.setEditMode();
        user.shouldSeeElement(mainPage.widgetSettingsHeader.resetButton);
        userWidget.clickOnResetButtonAndAcceptsAlert();
        userMode.shouldSeePlainMode();
    }


    @Test
    public void resetSettingsDuringEditing() {
        userMode.setEditMode();
        userWidget.deleteWidget(WidgetsData.NEWS);
        user.shouldSeeElement(mainPage.widgetSettingsHeader.resetButton);
        userWidget.clickOnResetButtonAndAcceptsAlert();
        userMode.shouldSeePlainMode();
    }

    @Test
    public void triesToResetSettingsAndStopIt() {
        userMode.setEditMode();
        userWidget.deleteWidget(WidgetsData.NEWS);
        user.shouldSeeElement(mainPage.widgetSettingsHeader.resetButton);
        userWidget.clickOnResetButtonAndRejectAlert();
        userMode.shouldSeeEditMode();
        userWidget.shouldNotSeeWidgetWithId(WidgetsData.NEWS.getWidgetId());
        userWidget.shouldSeeWidgetsInAmount(WidgetsData.DEFAULT_NUMBER_OF_WIDGETS - 2);
    }

    @Test
    public void resetSettingsAlertTextIsCorrect() {
        userMode.setEditMode();
        userWidget.deleteWidget(WidgetsData.NEWS);
        user.shouldSeeElement(mainPage.widgetSettingsHeader.resetButton);
        userWidget.clickOnResetButtonAndShouldSeeAlertWithText(
                getTranslation(RESET_INFO_MESSAGE, CONFIG.getLang()));
    }
}
