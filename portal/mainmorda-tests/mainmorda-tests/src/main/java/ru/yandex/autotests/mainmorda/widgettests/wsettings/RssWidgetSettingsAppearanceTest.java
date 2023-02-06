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
import ru.yandex.autotests.mainmorda.data.CommonSettingsData;
import ru.yandex.autotests.mainmorda.data.RSSWidgetsSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.RssSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.LENTARU;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.WidgetInfo;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 04.02.13
 */
@Aqua.Test(title = "Общие настройки RSS виджетов")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Rss")
public class RssWidgetSettingsAppearanceTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private RssSteps userRss = new RssSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(RSSWidgetsSettingsData.TEST_DATA);
    }

    private WidgetInfo widgetInfo;

    public RssWidgetSettingsAppearanceTest(WidgetInfo widgetInfo) {
        this.widgetInfo = widgetInfo;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        userWidget.addWidgetInEditMode(LENTARU.getName());
        user.shouldSeeElement(mainPage.rssWidget);
        user.clicksOn(mainPage.rssWidget.editIcon);
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
    public void closeCross() {
        user.shouldSeeElement(mainPage.widgetSettings.closeSettingsX);
        user.clicksOn(mainPage.widgetSettings.closeSettingsX);
        user.shouldNotSeeElement(mainPage.widgetSettings);
    }

    @Test
    public void typeText() {
        user.shouldSeeElement(mainPage.rssSettings.typeText);
        user.shouldSeeElementWithText(mainPage.rssSettings.typeText,
                RSSWidgetsSettingsData.TYPE_TEXT);
        user.clicksOn(mainPage.widgetSettings.closeSettingsX);
    }

    @Test
    public void heightText() {
        user.shouldSeeElement(mainPage.rssSettings.heightText);
        user.shouldSeeElementWithText(mainPage.rssSettings.heightText,
                RSSWidgetsSettingsData.HEIGHT_TEXT);
        user.clicksOn(mainPage.widgetSettings.closeSettingsX);
    }

    @Test
    public void noTextCheckbox() {
        user.shouldSeeElement(mainPage.rssSettings.noText);
        user.shouldSeeElementWithText(mainPage.rssSettings.noText,
                RSSWidgetsSettingsData.NO_TEXT);
        user.clicksOn(mainPage.widgetSettings.closeSettingsX);
    }

    @Test
    public void typeSelect() {
        user.shouldSeeElement(mainPage.rssSettings.type);
        userRss.shouldSeeSelectWithOptions(mainPage.rssSettings.type,
                RSSWidgetsSettingsData.TYPE_LIST);
        user.clicksOn(mainPage.widgetSettings.closeSettingsX);
    }

    @Test
    public void heightSelect() {
        user.shouldSeeElement(mainPage.rssSettings.height);
        userRss.shouldSeeSelectWithOptions(mainPage.rssSettings.height,
                RSSWidgetsSettingsData.HEIGHT_LIST);
        user.clicksOn(mainPage.widgetSettings.closeSettingsX);
    }

    @After
    public void after() {
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userMode.saveSettings();
    }
}
