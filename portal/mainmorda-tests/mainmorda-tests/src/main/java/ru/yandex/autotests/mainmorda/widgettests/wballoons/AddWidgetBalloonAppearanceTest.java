package ru.yandex.autotests.mainmorda.widgettests.wballoons;

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

import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SecurityMessages.WIDGET_ADD_INFO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SecurityMessages.WIDGET_ADD_INFO_EXTERNAL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SecurityMessages.WIDGET_NO_YANDEX;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetBalloon.WIDGET_ADD_DELETE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetBalloon.WIDGET_ADD_KEEP;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: alex89
 * Date: 27.12.12
 * Проверка балунов добавления виджета
 * -для чужого виджета
 * -для яндексовского виджета
 * в двух режимах (виджетном и редактирования) дизайн отличается
 */
@Aqua.Test(title = "Внешний вид балунов при добавлении виджетов")
@Features({"Main", "Widget", "Widget Balloon"})
@Stories("Add Widget")
public class AddWidgetBalloonAppearanceTest {
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
        userMode.setMode(WIDGET, mordaAllureBaseRule);
    }

    @Test
    public void addWidgetBalloonAppearanceForExternalWidgets() {
        userWidget.addWidgetWithoutAcception(WidgetsData.WAR_NEWS.getName());
        user.shouldSeeElement(mainPage.veil);
        user.shouldSeeElement(mainPage.addWidgetBalloon);
        user.shouldSeeElement(mainPage.addWidgetBalloon.addMessage);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addMessage,
                getTranslation(WIDGET_ADD_INFO_EXTERNAL, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.addButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addButton,
                getTranslation(WIDGET_ADD_KEEP, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.deleteButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.deleteButton,
                getTranslation(WIDGET_ADD_DELETE, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.noYandexMessage);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.noYandexMessage,
                getTranslation(WIDGET_NO_YANDEX, CONFIG.getLang()));

        userWidget.acceptWidgetAddition();
    }

    @Test
    public void addWidgetBalloonAppearanceForYandexWidgets() {
        userWidget.addWidgetWithoutAcception(WidgetsData.PHOTO.getName());
        user.shouldSeeElement(mainPage.veil);
        user.shouldSeeElement(mainPage.addWidgetBalloon);
        user.shouldSeeElement(mainPage.addWidgetBalloon.addMessage);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addMessage,
                getTranslation(WIDGET_ADD_INFO, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.addButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addButton,
                getTranslation(WIDGET_ADD_KEEP, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.deleteButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.deleteButton,
                getTranslation(WIDGET_ADD_DELETE, CONFIG.getLang()));

        user.shouldNotSeeElement(mainPage.addWidgetBalloon.noYandexMessage);
        userWidget.acceptWidgetAddition();
    }

    @Test
    public void addWidgetBalloonAppearanceForExternalWidgetsInEditMode() {
        userMode.setEditMode();
        userWidget.addWidgetInEditModeWithoutAcception(WidgetsData.WAR_NEWS.getName());
        user.shouldSeeElement(mainPage.veil);
        user.shouldSeeElement(mainPage.addWidgetBalloon);
        user.shouldSeeElement(mainPage.addWidgetBalloon.addMessage);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addMessage,
                getTranslation(WIDGET_ADD_INFO_EXTERNAL, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.addButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addButton,
                getTranslation(WIDGET_ADD_KEEP, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.deleteButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.deleteButton,
                getTranslation(WIDGET_ADD_DELETE, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.noYandexMessage);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.noYandexMessage,
                getTranslation(WIDGET_NO_YANDEX, CONFIG.getLang()));

        userWidget.acceptWidgetAddition();
    }

    @Test
    public void addWidgetBalloonAppearanceForYandexWidgetsInEditMode() {
        userMode.setEditMode();
        userWidget.addWidgetInEditModeWithoutAcception(WidgetsData.PHOTO.getName());
        user.shouldSeeElement(mainPage.veil);
        user.shouldSeeElement(mainPage.addWidgetBalloon);
        user.shouldSeeElement(mainPage.addWidgetBalloon.addMessage);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addMessage,
                getTranslation(WIDGET_ADD_INFO, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.addButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.addButton,
                getTranslation(WIDGET_ADD_KEEP, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.addWidgetBalloon.deleteButton);
        user.shouldSeeElementWithText(mainPage.addWidgetBalloon.deleteButton,
                getTranslation(WIDGET_ADD_DELETE, CONFIG.getLang()));

        user.shouldNotSeeElement(mainPage.addWidgetBalloon.noYandexMessage);
        userWidget.acceptWidgetAddition();
    }
}