package ru.yandex.autotests.mainmorda.widgettests.wproperties;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.SkinsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mainmorda.steps.SkinsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 03.12.12
 */
@Aqua.Test(title = "Проверка появления фейкового паттерна")
@Features({"Main", "Widget", "Pattern"})
@Stories("Patterns")
public class FakePatternTest {
    private static final Properties CONFIG = new Properties();
    private String skinId = SkinsData.RANDOM_SKIN;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, Mode.WIDGET),
                CONFIG.getBaseURL());
        userMode.resetSettings();
    }

    /**
     * Режим редактирования: когда ничего не настраивалось, паттерн не сохраняется
     */
    @Test
    public void fakePatternInCaseOfNoActionsInEditMode() {
        userMode.setEditMode(CONFIG.getBaseURL());
        userPattern.shouldSeeFakePatternRequest();
        user.shouldSeeElement(mainPage.widgetSettingsHeader.saveButton);
        user.clicksOn(mainPage.widgetSettingsHeader.saveButton);
        userMode.shouldSeeFakeMode();
    }

    /**
     * Режим редактирования: открываем настройку виджета и нажимаем 'OK', должен сформироваться фейковый паттерн
     */
    @Test
    public void fakePatternInCaseOfOpenWidgetSettingsAndApprove() {
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.newsBlock);
        user.shouldSeeElement(mainPage.newsBlock.editIcon);
        user.clicksOn(mainPage.newsBlock.editIcon);
        user.shouldSeeElement(mainPage.newsSettings);
        user.shouldSeeElement(mainPage.newsSettings.okButton);
        user.clicksOn(mainPage.newsSettings.okButton);

        userPattern.shouldSeeFakePatternRequest();

        user.shouldSeeElement(mainPage.widgetSettingsHeader.saveButton);
        user.clicksOn(mainPage.widgetSettingsHeader.saveButton);
        userMode.shouldSeeFakeMode();
    }

    /**
     * Режим редактирования: открываем настройку виджета и нажимаем 'Закрыть', должен сформироваться фейковый патерн
     */
    @Test
    public void fakePatternInCaseOfOpenWidgetSettingsAndClose() {
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.newsBlock);
        user.shouldSeeElement(mainPage.newsBlock.editIcon);
        user.clicksOn(mainPage.newsBlock.editIcon);
        user.shouldSeeElement(mainPage.newsSettings);
        user.shouldSeeElement(mainPage.newsSettings.closeSettingsButton);
        user.clicksOn(mainPage.newsSettings.closeSettingsButton);
        userPattern.shouldSeeFakePatternRequest();

        user.shouldSeeElement(mainPage.widgetSettingsHeader.saveButton);
        user.clicksOn(mainPage.widgetSettingsHeader.saveButton);
        userMode.shouldSeeFakeMode();
    }

    /**
     * Устанавливаем скин.
     * Открываем режим редактирования:  должен сформироваться фейковый патерн
     */
    @Test
    public void fakePatternInCaseOfSkin() {
        userSkins.savesSkinWithUrl(skinId);
        userSkins.shouldSeeSkin(skinId);
        userMode.setEditMode(CONFIG.getBaseURL());
        userPattern.shouldSeeFakePatternRequestForSkin(skinId);
        user.shouldSeeElement(mainPage.widgetSettingsHeader.saveButton);
        user.clicksOn(mainPage.widgetSettingsHeader.saveButton);
        userMode.shouldSeeFakeMode();
    }
}

