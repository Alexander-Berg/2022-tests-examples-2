package ru.yandex.autotests.mainmorda.commontests.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.HeaderData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.HEADER;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;


/**
 * User: eoff
 * Date: 18.01.13
 */
@Aqua.Test(title = "Проверка ссылки 'Личные настройки' в хидере и попапа с выбранной темой")
@Features({"Main", "Common", "Header"})
@Stories("Setup Link")
public class HeaderSetupLinkThemeTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.opensPage(HeaderData.SET_THEME_URL_PATTERN + CookieManager.getSecretKey(driver), CONFIG.getBaseURL());
    }

    @Test
    public void setupLinkTheme() {
        userLink.shouldSeeLink(mainPage.headerBlock.setupLink, HeaderData.SETUP_LINK, HEADER);
    }

    @Test
    public void setupPopupSetupLinkTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupThemePopUp.setUpYandex,
                HeaderData.SETUP_YANDEX_LINK, HEADER);
    }

    @Test
    public void setupPopupAddWidgetLinkTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupThemePopUp.addWidget,
                HeaderData.ADD_WIDGET_LINK, HEADER);
    }

    @Test
    public void setupPopupSetThemeLinkTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupThemePopUp.setThemeLink,
                HeaderData.SET_THEME_LINK, HEADER);
    }

    @Test
    public void setupPopupDropThemeLinkTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        //todo: find a better solution to update expected href on runtime
        HeaderData.DROP_THEME_LINK.attributes = hasAttribute(HtmlAttribute.HREF,
                equalTo(HeaderData.DROP_THEME_HREF_PATTERN + CookieManager.getSecretKey(driver)));
        userLink.shouldSeeLink(mainPage.headerBlock.setupThemePopUp.dropThemeLink,
                HeaderData.DROP_THEME_LINK, HEADER);
    }

    @Test
    public void setupPopupOtherSettingsLinkTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupThemePopUp.otherSettingsLink,
                HeaderData.OTHER_SETTINGS_LINK, HEADER);
    }

    @Test
    public void setupPopupChangeCityLink() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupThemePopUp.changeCityLink,
                HeaderData.CHANGE_CITY_LINK, HEADER);
    }

    @Test
    public void setupPopupThemeSize() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        user.shouldSeeElement(mainPage.headerBlock.setupThemePopUp.otherSettingsLink);
        user.shouldSeeListWithSize(mainPage.headerBlock.setupThemePopUp.allLinks,
                equalTo(HeaderData.SETUP_POPUP_THEME_SIZE));
    }
}
