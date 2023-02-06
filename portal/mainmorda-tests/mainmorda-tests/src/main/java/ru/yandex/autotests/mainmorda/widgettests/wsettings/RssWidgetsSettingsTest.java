package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.RSSWidgetsSettingsData;
import ru.yandex.autotests.mainmorda.data.WidgetsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.RssSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 04.02.13
 */
@Aqua.Test(title = "Настройки RSS виджетов")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Rss")
public class RssWidgetsSettingsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private RssSteps userRss = new RssSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        userWidget.addWidgetInEditMode(WidgetsData.LENTARU.getName());
        user.shouldSeeElement(mainPage.rssWidget);
        user.clicksOn(mainPage.rssWidget.editIcon);
        user.shouldSeeElement(mainPage.rssSettings);
    }

    @Test
    public void noTextCheckBox() {
        user.shouldSeeElement(mainPage.rssSettings.noText);
        user.deselectElement(mainPage.rssSettings.noText);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userRss.shouldSeeDescriptions();
        user.clicksOn(mainPage.rssWidget.editIcon);
        user.shouldSeeElement(mainPage.rssSettings);
        user.shouldSeeElement(mainPage.rssSettings.noText);
        user.selectElement(mainPage.rssSettings.noText);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        userRss.shouldNotSeeDescriptions();
    }

    @Test
    public void heightChanges() {
        user.shouldSeeElement(mainPage.rssSettings.height);
        user.selectOption(mainPage.rssSettings.height, RSSWidgetsSettingsData.SET_SIZE_GENERIC);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElementMatchingTo(mainPage.rssWidget.rssBody,
                hasAttribute(HtmlAttribute.CLASS, RSSWidgetsSettingsData.HEIGHT_GENERIC_DIV));
        user.clicksOn(mainPage.rssWidget.editIcon);
        user.shouldSeeElement(mainPage.rssSettings.height);
        user.selectOption(mainPage.rssSettings.height, RSSWidgetsSettingsData.SET_SIZE_COMPACT);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElementMatchingTo(mainPage.rssWidget.rssBody,
                hasAttribute(HtmlAttribute.CLASS, RSSWidgetsSettingsData.HEIGHT_COMPACT_DIV));
        user.clicksOn(mainPage.rssWidget.editIcon);
        user.shouldSeeElement(mainPage.rssSettings.height);
        user.selectOption(mainPage.rssSettings.height, RSSWidgetsSettingsData.SET_SIZE_LARGE);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElementMatchingTo(mainPage.rssWidget.rssBody,
                hasAttribute(HtmlAttribute.CLASS, RSSWidgetsSettingsData.HEIGHT_BIG_DIV));
    }

    @Test
    public void newsWithImages() {
        user.shouldSeeElement(mainPage.rssSettings.type);
        user.selectOption(mainPage.rssSettings.type, RSSWidgetsSettingsData.SET_TYPE_TEXT_IMG);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.rssWidget.rssBodyId);
        user.shouldSeeElementMatchingTo(mainPage.rssWidget.rssBodyId,
                hasAttribute(HtmlAttribute.CLASS, RSSWidgetsSettingsData.TYPE_TEXT_IMG_DIV));
        userRss.shouldSeeImages();
        user.clicksOn(mainPage.rssWidget.editIcon);
        user.shouldSeeElement(mainPage.rssSettings);
        user.shouldSeeElement(mainPage.rssSettings.type);
        user.selectOption(mainPage.rssSettings.type, RSSWidgetsSettingsData.SET_TYPE_TEXT);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.rssWidget.rssBodyId);
        user.shouldSeeElementMatchingTo(mainPage.rssWidget.rssBodyId,
                hasAttribute(HtmlAttribute.CLASS, RSSWidgetsSettingsData.TYPE_TEXT_DIV));
        userRss.shouldNotSeeImages();
    }

    @Test
    public void newsMagazine() {
        user.shouldSeeElement(mainPage.rssSettings.type);
        user.selectOption(mainPage.rssSettings.type, RSSWidgetsSettingsData.SET_TYPE_MAGAZINE);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.rssWidget.rssBodyId);
        user.shouldSeeElementMatchingTo(mainPage.rssWidget.rssBodyId,
                hasAttribute(HtmlAttribute.CLASS, RSSWidgetsSettingsData.TYPE_MAGAZINE_DIV));
        userRss.shouldSeeImages();
        user.clicksOn(mainPage.rssWidget.editIcon);
        user.shouldSeeElement(mainPage.rssSettings);
        user.shouldSeeElement(mainPage.rssSettings.type);
        user.selectOption(mainPage.rssSettings.type, RSSWidgetsSettingsData.SET_TYPE_TEXT);
        user.clicksOn(mainPage.rssSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.rssWidget.rssBodyId);
        user.shouldSeeElementMatchingTo(mainPage.rssWidget.rssBodyId,
                hasAttribute(HtmlAttribute.CLASS, RSSWidgetsSettingsData.TYPE_TEXT_DIV));
        userRss.shouldNotSeeImages();
    }

}
