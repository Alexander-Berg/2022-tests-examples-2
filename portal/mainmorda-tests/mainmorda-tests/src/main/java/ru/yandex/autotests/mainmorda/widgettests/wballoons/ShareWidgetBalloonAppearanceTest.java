package ru.yandex.autotests.mainmorda.widgettests.wballoons;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
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
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetShare.WIDGETSHARE_CLOSE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetShare.WIDGETSHARE_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetShare.WIDGETSHARE_VK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.WidgetPopup.SHARE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: alex89
 * Date: 09.01.13
 */

@Aqua.Test(title = "Внешний вид балуна 'Поделиться виджетом'")
@Features({"Main", "Widget", "Widget Balloon"})
@Stories("Share Widget")
public class ShareWidgetBalloonAppearanceTest {
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
    public void shareWidgetBalloonAppearance() {
        Widget widgetHtml = userWidget.shouldSeeWidgetWithId(LENTARU.getWidgetId());
        userWidget.clicksOnShareButtonForWidget(widgetHtml);
        userWidget.elementExists(mainPage.iframeVeil);
        user.shouldSeeElement(mainPage.shareWidgetBalloon);
        user.shouldSeeElement(mainPage.shareWidgetBalloon.shareHead);
        user.shouldSeeElementWithText(mainPage.shareWidgetBalloon.shareHead,
                getTranslation(WIDGETSHARE_TITLE, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.shareWidgetBalloon.linkInput);
        user.shouldSeeInputWithText(mainPage.shareWidgetBalloon.linkInput,
                String.format(WBalloonsData.SHARE_LINK_URL_PATTERN, CONFIG.getProtocol(), CONFIG.getBaseDomain(), LENTARU.getName()));

        user.shouldSeeElement(mainPage.shareWidgetBalloon.infoText);
        user.shouldSeeElementWithText(mainPage.shareWidgetBalloon.infoText,
                getTranslation(SHARE, CONFIG.getLang()));

        user.shouldSeeElement(mainPage.shareWidgetBalloon.closeButton);
        user.shouldSeeElementWithText(mainPage.shareWidgetBalloon.closeButton,
                getTranslation(WIDGETSHARE_CLOSE, CONFIG.getLang()));
        user.clicksOn(mainPage.shareWidgetBalloon.closeButton);
        user.shouldNotSeeElement(mainPage.shareWidgetBalloon);
    }

    @Test
    public void shareWidgetBalloonSocialIcons() {
        Widget widgetHtml = userWidget.shouldSeeWidgetWithId(LENTARU.getWidgetId());
        userWidget.clicksOnShareButtonForWidget(widgetHtml);
        userWidget.elementExists(mainPage.iframeVeil);
        user.shouldSeeElement(mainPage.shareWidgetBalloon);

        user.shouldSeeElement(mainPage.shareWidgetBalloon.vkIcon);
        user.shouldSeeElementMatchingTo(mainPage.shareWidgetBalloon.vkIcon,
                hasAttribute(HtmlAttribute.TITLE, equalTo(getTranslation(WIDGETSHARE_VK, CONFIG.getLang()))));

        user.shouldSeeElement(mainPage.shareWidgetBalloon.fbIcon);
//        user.shouldSeeElementMatchingTo(mainPage.shareWidgetBalloon.fbIcon,
//                hasAttribute(HtmlAttribute.TITLE, equalTo(getTranslation(WIDGETSHARE_FB, CONFIG.getLang()))));

        user.shouldSeeElement(mainPage.shareWidgetBalloon.twIcon);
//        user.shouldSeeElementMatchingTo(mainPage.shareWidgetBalloon.twIcon,
//                hasAttribute(HtmlAttribute.TITLE, equalTo(getTranslation(WIDGETSHARE_TW, CONFIG.getLang()))));

        user.shouldSeeElement(mainPage.shareWidgetBalloon.closeCross);
        user.clicksOn(mainPage.shareWidgetBalloon.closeCross);
        user.shouldNotSeeElement(mainPage.shareWidgetBalloon);
    }
}
