package ru.yandex.autotests.mainmorda.widgettests.wheader;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.WidgetHeaderData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.mainmorda.data.WidgetHeaderData.TEST_REGION;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 17.01.13
 */
@Aqua.Test(title = "Header настройки страницы (внешний вид)")
@Features({"Main", "Widget", "Widget Header"})
public class WidgetSettingsHeaderAppearanceTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), TEST_REGION, CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode();
    }

    @Test
    public void saveButtonText() {
        user.shouldSeeElement(mainPage.widgetSettingsHeader.saveButton);
        user.shouldSeeElementWithText(mainPage.widgetSettingsHeader.saveButton,
                WidgetHeaderData.SAVE_TEXT);
    }

    @Test
    public void resetButtonText() {
        user.shouldSeeElement(mainPage.widgetSettingsHeader.resetButton);
        user.shouldSeeElementWithText(mainPage.widgetSettingsHeader.resetButton,
                WidgetHeaderData.RESET_TEXT);
    }

    @Test
    public void cancelButtonText() {
        user.shouldSeeElement(mainPage.widgetSettingsHeader.cancelButton);
        user.shouldSeeElementWithText(mainPage.widgetSettingsHeader.cancelButton,
                WidgetHeaderData.CANCEL_TEXT);
    }

    @Test
    public void undoButtonText() {
        user.shouldNotSeeElement(mainPage.widgetSettingsHeader.undoButton);
        user.shouldSeeElement(mainPage.teaserBlock);
        user.shouldSeeElement(mainPage.teaserBlock.closeCross);
        user.clicksOn(mainPage.teaserBlock.closeCross);
        user.shouldNotSeeElement(mainPage.teaserBlock);
        user.shouldSeeElement(mainPage.widgetSettingsHeader.undoButton);
        user.shouldSeeElementWithText(mainPage.widgetSettingsHeader.undoButton,
                WidgetHeaderData.UNDO_TEXT_MATCHER);
    }

    @Test
    public void addNewWidgetText() {
        user.shouldSeeElement(mainPage.widgetSettingsHeader.inCatalogWidgets);
        user.shouldSeeElementWithText(mainPage.widgetSettingsHeader.inCatalogWidgets,
                WidgetHeaderData.ADD_WIDGET_TEXT);
    }

}
