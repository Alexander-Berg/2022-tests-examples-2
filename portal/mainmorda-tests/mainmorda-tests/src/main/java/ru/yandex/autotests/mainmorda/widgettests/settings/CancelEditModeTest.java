package ru.yandex.autotests.mainmorda.widgettests.settings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 11.01.13
 * При клике по 'Отменить' настройки закрываются, морда не изменяет состояния.
 * Плоская морда остается плоской, виджетная -- виджетной.
 */

@Aqua.Test(title = "Закрытие настроек (Отменить)")
@Features({"Main", "Widget", "Settings"})
@Stories("Cancel edit")
public class CancelEditModeTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void cancelEditModeOnPlainMordaAuth() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, WIDGET),
                CONFIG.getBaseURL());
        userMode.resetSettings();
        userMode.setEditMode();
        user.shouldSeeElement(mainPage.widgetSettingsHeader.cancelButton);
        user.clicksOn(mainPage.widgetSettingsHeader.cancelButton);
        userMode.shouldSeePlainMode();
    }

    @Test
    public void cancelEditModeOnWidgetMordaAuth() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, WIDGET),
                CONFIG.getBaseURL());
        userMode.setModeLogged(WIDGET);
        userMode.setEditMode();
        user.shouldSeeElement(mainPage.widgetSettingsHeader.cancelButton);
        user.clicksOn(mainPage.widgetSettingsHeader.cancelButton);
        userMode.shouldSeeWidgetMode();
    }

    @Test
    public void cancelEditModeOnPlainMorda() {
        userMode.setEditMode();
        user.shouldSeeElement(mainPage.widgetSettingsHeader.cancelButton);
        user.clicksOn(mainPage.widgetSettingsHeader.cancelButton);
        userMode.shouldSeePlainMode();
    }

    @Test
    public void cancelEditModeOnWidgetMorda() {
        userMode.setWidgetMode();
        userMode.setEditMode();
        user.shouldSeeElement(mainPage.widgetSettingsHeader.cancelButton);
        user.clicksOn(mainPage.widgetSettingsHeader.cancelButton);
        userMode.shouldSeeWidgetMode();
    }
}
