package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.Widget;
import ru.yandex.autotests.mainmorda.data.CommonSettingsData;
import ru.yandex.autotests.mainmorda.data.WidgetsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static org.junit.Assume.assumeFalse;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 14.12.12
 */
@Aqua.Test(title = "Общие настройки виджетов")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Common Settings")
public class CommonSettingsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(WidgetsData.COMMON_EDITABLE_WIDGETS);
    }

    private WidgetsData.WidgetInfo info;
    private Widget widget;

    public CommonSettingsTest(WidgetsData.WidgetInfo info) {
        this.info = info;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        widget = userWidget.shouldEditableSeeWidgetWithId(info.getWidgetId());
        user.shouldSeeElement(widget);
        user.clicksOn(widget.editIcon);
        user.shouldSeeElement(mainPage.widgetSettings);
    }

    @Test
    public void closeButton() {
        user.shouldSeeElement(mainPage.widgetSettings.closeSettingsButton);
        user.shouldSeeElementWithText(mainPage.widgetSettings.closeSettingsButton,
                CommonSettingsData.CLOSE_TEXT);
        user.clicksOn(mainPage.widgetSettings.closeSettingsButton);
    }

    @Test
    public void okButton() {
        user.shouldSeeElement(mainPage.widgetSettings.okButton);
        user.shouldSeeElementWithText(mainPage.widgetSettings.okButton,
                CommonSettingsData.OK_TEXT);
        user.clicksOn(mainPage.widgetSettings.okButton);
    }

    @Test
    public void resetButton() {
        user.shouldSeeElement(mainPage.widgetSettings.resetSettingsButton);
        user.shouldSeeElementWithText(mainPage.widgetSettings.resetSettingsButton,
                CommonSettingsData.RESET_TEXT);
        user.clicksOn(mainPage.widgetSettings.resetSettingsButton);
    }

    @Test
    public void setupTitleText() {
        user.shouldSeeElement(mainPage.widgetSettings.setupTitle);
        user.shouldSeeElementWithText(mainPage.widgetSettings.setupTitle,
                CommonSettingsData.SETTINGS_TITLE);
        user.clicksOn(mainPage.widgetSettings.resetSettingsButton);
    }

    @Test
    public void autoReloadCheckBox() {
        user.shouldSeeElement(mainPage.widgetSettings.autoReloadCheckbox);
        user.shouldSeeElementWithText(mainPage.widgetSettings.autoReloadCheckbox,
                CommonSettingsData.AUTO_RELOAD);
        user.shouldSeeElementIsSelected(mainPage.widgetSettings.autoReloadCheckbox);
        user.clicksOn(mainPage.widgetSettings.resetSettingsButton);
    }

    @Test
    public void closeCross() {
        user.shouldSeeElement(mainPage.widgetSettings.closeSettingsX);
        user.clicksOn(mainPage.widgetSettings.closeSettingsX);
        user.shouldNotSeeElement(mainPage.widgetSettings);
    }

    @After
    public void after() {
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userMode.saveSettings();
        user.shouldSeePage(CONFIG.getBaseURL());
    }
}
