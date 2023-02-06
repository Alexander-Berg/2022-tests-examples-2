package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TrafficSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TrafficSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;


/**
 * User: eoff
 * Date: 25.12.12
 */
@Aqua.Test(title = "Внешний вид настроек пробок")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Traffic")
public class TrafficSettingsAppearanceTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TrafficSteps userTraffic = new TrafficSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userTraffic.ifFull();
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode();
        user.shouldSeeElement(mainPage.trafficFullBlock);
        user.shouldSeeElement(mainPage.trafficFullBlock.editIcon);
        user.clicksOn(mainPage.trafficFullBlock.editIcon);
        user.shouldSeeElement(mainPage.trafficSettings);
        userTraffic.switchToTrafficFrame();
    }

    @Test
    public void saveText() {
        user.shouldSeeElement(mainPage.trafficSettings.buttonsBlock.saveButton);
    }

    @Test
    public void cancelText() {
        user.shouldSeeElement(mainPage.trafficSettings.buttonsBlock.cancelButton);
        user.shouldSeeElementWithText(mainPage.trafficSettings.buttonsBlock.cancelButton,
                TrafficSettingsData.CANCEL_BUTTON_TEXT);
    }

    @Test
    public void resetText() {
        user.shouldSeeElement(mainPage.trafficSettings.buttonsBlock.resetButton);
        user.shouldSeeElementWithText(mainPage.trafficSettings.buttonsBlock.resetButton,
                TrafficSettingsData.RESET_BUTTON_TEXT);
    }

    @Test
    public void homeText() {
        user.shouldSeeElement(mainPage.trafficSettings.homeText);
        user.shouldSeeElementWithText(mainPage.trafficSettings.homeText,
                TrafficSettingsData.HOME_TEXT);
    }

    @Test
    public void workText() {
        user.shouldSeeElement(mainPage.trafficSettings.workText);
        user.shouldSeeElementWithText(mainPage.trafficSettings.workText,
                TrafficSettingsData.WORK_TEXT);
    }

    @Test
    public void infoText() {
        user.shouldSeeElement(mainPage.trafficSettings.infoText);
        user.shouldSeeElementWithText(mainPage.trafficSettings.infoText,
                TrafficSettingsData.INFO_TEXT);
    }

    @Test
    public void titleText() {
        user.shouldSeeElement(mainPage.trafficSettings.titleText);
        user.shouldSeeElementWithText(mainPage.trafficSettings.titleText,
                TrafficSettingsData.TITLE_TEXT);
    }
}
