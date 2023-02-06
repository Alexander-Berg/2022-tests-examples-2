package ru.yandex.autotests.turkey.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.turkey.data.HeaderData.CLID;
import static ru.yandex.autotests.turkey.data.HeaderData.SET_HOME_POPUP_ICON_TEXT;
import static ru.yandex.autotests.turkey.data.HeaderData.SET_HOME_POPUP_LINK_HREF_PATTERN;
import static ru.yandex.autotests.turkey.data.HeaderData.SET_HOME_POPUP_TEXT;
import static ru.yandex.autotests.turkey.data.HeaderData.SET_HOME_TEXT;
import static ru.yandex.autotests.turkey.data.HeaderData.SET_HOME_HREF;

/**
 * User: alex89
 * Date: 10.07.12
 */
@Aqua.Test(title = "Проверка ссылки 'Сделать Яндекс стартовой страницей' и её исчезновения по clid-у")
@Features("Header")
@Stories("Clid")
public class ClidTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.shouldSeeElement(yandexComTrPage.headerBlock);
    }

    @Test
    public void setHomeLinkIsPresentedByDefault() {
        user.shouldSeeElementWithText(yandexComTrPage.headerBlock.setHomeLink, SET_HOME_TEXT);
        user.shouldSeeElementMatchingTo(yandexComTrPage.headerBlock.setHomeLink, hasAttribute(HtmlAttribute.HREF, SET_HOME_HREF));
        user.clicksOn(yandexComTrPage.headerBlock.setHomeLink);
        user.shouldSeePage(CONFIG.getBaseURL());
    }

//    @Test
    public void setHomePopUpElements() {
        user.shouldSeeElement(yandexComTrPage.headerBlock.setHomeLink);
        user.clicksOn(yandexComTrPage.headerBlock.setHomeLink);
        user.shouldSeeElement(yandexComTrPage.headerBlock.setHomePopUp);
        user.shouldSeeElement(yandexComTrPage.headerBlock.setHomePopUp.popUpText);
        user.shouldSeeElementWithText(yandexComTrPage.headerBlock.setHomePopUp.popUpText,
                SET_HOME_POPUP_TEXT);
        user.shouldSeeElement(yandexComTrPage.headerBlock.setHomePopUp.popUpIcon);
        user.shouldSeeElement(yandexComTrPage.headerBlock.setHomePopUp.popUpIconText);
        user.shouldSeeElementWithText(yandexComTrPage.headerBlock.setHomePopUp.popUpIconText,
                SET_HOME_POPUP_ICON_TEXT);
        user.shouldSeeElement(yandexComTrPage.headerBlock.setHomePopUp.popUpIconLink);
        user.shouldSeeElementMatchingTo(yandexComTrPage.headerBlock.setHomePopUp.popUpIconLink,
                hasAttribute(HtmlAttribute.HREF, SET_HOME_POPUP_LINK_HREF_PATTERN));
    }

}

