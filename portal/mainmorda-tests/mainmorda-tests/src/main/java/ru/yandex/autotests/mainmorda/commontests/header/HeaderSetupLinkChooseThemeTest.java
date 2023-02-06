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
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.HEADER;

/**
 * User: eoff
 * Date: 18.01.13
 */
@Aqua.Test(title = "Проверка ссылки 'Личные настройки' в хидере выбора темы и попапа")
@Features({"Main", "Common", "Header"})
@Stories("Setup Link")
public class HeaderSetupLinkChooseThemeTest {
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
        user.shouldSeeElement(mainPage.headerBlock);
        user.clicksOn(mainPage.headerBlock.setupLink);
        user.shouldSeeElement(mainPage.headerBlock.setupMainPopUp.setThemeLink);
        user.clicksOn(mainPage.headerBlock.setupMainPopUp.setThemeLink);
        user.shouldSeePage(HeaderData.SET_THEME_LINK.url);
    }

    @Test
    public void setupLink() {
        userLink.shouldSeeLink(mainPage.headerBlock.setupLink, HeaderData.SETUP_THEME_LINK, HEADER);
    }

    @Test
    public void setupPopupChangeCityLinkChooseTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupChooseThemePopUp.changeCityLink,
                HeaderData.CHANGE_CITY_THEMES_LINK, HEADER);
    }

    @Test
    public void setupPopupOtherSettingsLinkChooseTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupChooseThemePopUp.otherSettingsLink,
                HeaderData.OTHER_SETTINGS_THEME_LINK, HEADER);
    }

    @Test
    public void setupPopupSetThemeTextChooseTheme() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        user.shouldSeeElement(mainPage.headerBlock.setupChooseThemePopUp.setThemeText);
        user.shouldSeeElementWithText(mainPage.headerBlock.setupChooseThemePopUp.setThemeText,
                HeaderData.SET_THEME_LINK.text);
    }

    @Test
    public void setupPopupChooseThemeSize() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        user.shouldSeeElement(mainPage.headerBlock.setupChooseThemePopUp.otherSettingsLink);
        user.shouldSeeListWithSize(mainPage.headerBlock.setupChooseThemePopUp.allLinks,
                equalTo(HeaderData.SETUP_POPUP_CHOOSE_THEME_SIZE));
    }

}
