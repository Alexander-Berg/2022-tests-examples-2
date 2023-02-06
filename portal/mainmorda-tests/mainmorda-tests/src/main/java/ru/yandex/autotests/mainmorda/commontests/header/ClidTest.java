package ru.yandex.autotests.mainmorda.commontests.header;

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
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.HeaderData.CLID;
import static ru.yandex.autotests.mainmorda.data.HeaderData.SET_HOME_HREF;
import static ru.yandex.autotests.mainmorda.data.HeaderData.SET_HOME_POPUP_ICON_TEXT;
import static ru.yandex.autotests.mainmorda.data.HeaderData.SET_HOME_POPUP_LINK_HREF_PATTERN;
import static ru.yandex.autotests.mainmorda.data.HeaderData.SET_HOME_POPUP_TEXT;
import static ru.yandex.autotests.mainmorda.data.HeaderData.SET_HOME_TEXT;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;

/**
 * User: alex89
 * Date: 10.07.12
 */
@Aqua.Test(title = "Проверка ссылки 'Сделать Яндекс стартовой страницей' и её исчезновения по clid-у")
@Features({"Main", "Common", "Header"})
@Stories("Clid")
public class ClidTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.headerBlock);
    }

    @Test
    public void setHomeLinkIsPresentedByDefault() {
        user.shouldSeeElement(mainPage.headerBlock.setHomeText);
        user.shouldSeeElementWithText(mainPage.headerBlock.setHomeText, SET_HOME_TEXT);
        user.shouldSeeElement(mainPage.headerBlock.setHomeLink);
        user.shouldSeeElementMatchingTo(mainPage.headerBlock.setHomeLink, hasAttribute(HtmlAttribute.HREF, SET_HOME_HREF));
        user.clicksOn(mainPage.headerBlock.setHomeLink);
        user.shouldSeePage(CONFIG.getBaseURL());
    }

//    @Test
    public void setHomePopUpElements() {
        user.shouldSeeElement(mainPage.headerBlock.setHomeLink);
        user.clicksOn(mainPage.headerBlock.setHomeLink);
        user.shouldSeeElement(mainPage.headerBlock.setHomePopUp);
        user.shouldSeeElement(mainPage.headerBlock.setHomePopUp.popUpText);
        user.shouldSeeElementWithText(mainPage.headerBlock.setHomePopUp.popUpText,
                SET_HOME_POPUP_TEXT);
        user.shouldSeeElement(mainPage.headerBlock.setHomePopUp.popUpIcon);
        user.shouldSeeElement(mainPage.headerBlock.setHomePopUp.popUpIconText);
        user.shouldSeeElementWithText(mainPage.headerBlock.setHomePopUp.popUpIconText,
                SET_HOME_POPUP_ICON_TEXT);
        user.shouldSeeElement(mainPage.headerBlock.setHomePopUp.popUpIconLink);
        user.shouldSeeElementMatchingTo(mainPage.headerBlock.setHomePopUp.popUpIconLink,
                hasAttribute(HtmlAttribute.HREF, SET_HOME_POPUP_LINK_HREF_PATTERN));
    }

    @Test
    public void setHomeLinkIsNotPresentInClid() {
        user.opensPage(CONFIG.getBaseURL() + CLID, CONFIG.getBaseURL());
        user.shouldNotSeeElement(mainPage.headerBlock.setHomeLink);
        user.opensPage(CONFIG.getBaseURL());
        user.shouldNotSeeElement(mainPage.headerBlock.setHomeLink);
    }
}

