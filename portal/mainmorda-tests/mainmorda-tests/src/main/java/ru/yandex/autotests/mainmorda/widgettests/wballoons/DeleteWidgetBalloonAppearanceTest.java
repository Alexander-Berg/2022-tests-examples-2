package ru.yandex.autotests.mainmorda.widgettests.wballoons;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.Widget;
import ru.yandex.autotests.mainmorda.data.WBalloonsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.LENTARU;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetBalloon.WIDGET_DELETE_COMPLAIN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetBalloon.WIDGET_DELETE_DELETE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetBalloon.WIDGET_DELETE_INFO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetBalloon.WIDGET_CANCEL;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: alex89
 * Date: 27.12.12
 */
@Aqua.Test(title = "Внешний вид балунов при удалении виджетов")
@Features({"Main", "Widget", "Widget Balloon"})
@Stories("Delete Widget")
public class DeleteWidgetBalloonAppearanceTest {
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
        userWidget.addWidget(LENTARU.getName());
    }

    @Test
    public void deleteWidgetBalloonAppearanceForExternalWidgets() {
        Widget widgetHtml = userWidget.shouldSeeWidgetWithId(LENTARU.getWidgetId());
        user.moveMouseOn(widgetHtml);
        userWidget.deleteWidget(LENTARU);

        userWidget.elementExists(mainPage.iframeVeil);
        user.shouldSeeElement(mainPage.deleteWidgetBalloon);
        user.shouldSeeElement(mainPage.deleteWidgetBalloon.deleteMessage);
        user.shouldSeeElementWithText(mainPage.deleteWidgetBalloon.deleteMessage,
                getTranslation(WIDGET_DELETE_INFO, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.deleteWidgetBalloon.deleteButton);
        user.shouldSeeElementWithText(mainPage.deleteWidgetBalloon.deleteButton,
                getTranslation(WIDGET_DELETE_DELETE, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.deleteWidgetBalloon.keepButton);
        user.shouldSeeElementWithText(mainPage.deleteWidgetBalloon.keepButton,
                getTranslation(WIDGET_CANCEL, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.deleteWidgetBalloon.complainsLink);
        user.shouldSeeElementWithText(mainPage.deleteWidgetBalloon.complainsLink,
                getTranslation(WIDGET_DELETE_COMPLAIN, CONFIG.getLang()));
        user.shouldSeeElementMatchingTo(mainPage.deleteWidgetBalloon.complainsLink,
                hasAttribute(HtmlAttribute.HREF, equalTo(WBalloonsData.FEEDBACK_HREF + LENTARU.getName())));
    }
}
