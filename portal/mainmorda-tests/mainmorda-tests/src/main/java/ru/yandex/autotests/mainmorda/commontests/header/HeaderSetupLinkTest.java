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
@Aqua.Test(title = "Проверка ссылки 'Личные настройки' в хидере и попапа")
@Features({"Main", "Common", "Header"})
@Stories("Setup Link")
public class HeaderSetupLinkTest {
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
    }


    @Test
    public void setupLink() {
        userLink.shouldSeeLink(mainPage.headerBlock.setupLink, HeaderData.SETUP_LINK, HEADER);
    }

    @Test
    public void setupPopupSetupLink() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupMainPopUp.setUpYandex,
                HeaderData.SETUP_YANDEX_LINK, HEADER);
    }

    @Test
    public void setupPopupAddWidgetLink() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupMainPopUp.addWidget,
                HeaderData.ADD_WIDGET_LINK, HEADER);
    }

    @Test
    public void setupPopupSetThemeLink() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupMainPopUp.setThemeLink,
                HeaderData.SET_THEME_LINK, HEADER);
    }

    @Test
    public void setupPopupChangeCityLink() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupMainPopUp.changeCityLink,
                HeaderData.CHANGE_CITY_LINK, HEADER);
    }

    @Test
    public void setupPopupOtherSettingsLink() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        userLink.shouldSeeLink(mainPage.headerBlock.setupMainPopUp.otherSettingsLink,
                HeaderData.OTHER_SETTINGS_LINK, HEADER);
    }

    @Test
    public void setupPopupSize() {
        user.clicksOn(mainPage.headerBlock.setupLink);
        user.shouldSeeElement(mainPage.headerBlock.setupMainPopUp.otherSettingsLink);
        user.shouldSeeListWithSize(mainPage.headerBlock.setupMainPopUp.allLinks,
                equalTo(HeaderData.SETUP_POPUP_SIZE));
    }
}
