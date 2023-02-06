package ru.yandex.autotests.mainmorda.commontests.header;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import org.xml.sax.SAXException;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.HeaderData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.HeaderSteps;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.xml.parsers.ParserConfigurationException;
import java.io.IOException;

import static org.hamcrest.text.IsEqualIgnoringCase.equalToIgnoringCase;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.HEADER;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: eoff
 * Date: 21.01.13
 */
@Aqua.Test(title = "Проверка переключалки языка в header-е")
@Features({"Main", "Common", "Header"})
@Stories("Lang Switcher")
public class HeaderLangSwitcherTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private HeaderSteps userHeader = new HeaderSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(HeaderData.LANG_CITY);
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.headerBlock);
    }

    @Test
    public void defaultLanguage() {
        user.shouldSeeElement(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcher, HeaderData.DEFAULT_LANG_CODE);
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcher,
                HeaderData.DEFAULT_LANG_SWITCHER_LINK, HEADER);
    }

    @Test
    public void popupDefaultLanguage() {
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp.currentLang);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcherPopUp.currentLang,
                equalToIgnoringCase(HeaderData.DEFAULT_LANG_CODE));
    }

    @Test
    public void popupNationalLanguage() {
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp);
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcherPopUp.secondLang,
                HeaderData.NATIONAL_LANG_LINK, HEADER);
        user.clicksOn(mainPage.headerBlock.langSwitcherPopUp.secondLang);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcher, HeaderData.NATIONAL_LANG_CODE);
    }

    @Test
    public void popupMoreLangLink() {
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp);
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcherPopUp.more,
                HeaderData.MORE_LANG_LINK, HEADER);
    }

    @Test
    public void popupThirdLanguage() {
        user.setsLanguage(HeaderData.THIRD_LANG);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcher, HeaderData.THIRD_LANG_CODE);
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcher,
                HeaderData.THIRD_LANG_SWITCHER_LINK, HEADER);
    }

    @Test
    public void popupThreeLangDefault() {
        user.setsLanguage(HeaderData.THIRD_LANG);
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherExtPopUp);
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcherExtPopUp.defaultLang,
                HeaderData.DEFAULT_LANG_LINK, HEADER);
        user.clicksOn(mainPage.headerBlock.langSwitcherExtPopUp.defaultLang);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcher, HeaderData.DEFAULT_LANG_CODE);
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcherPopUp.currentLang,
                equalToIgnoringCase(HeaderData.DEFAULT_LANG_CODE));
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcherPopUp.secondLang,
                HeaderData.NATIONAL_LANG_LINK, HEADER);
    }

    @Test
    public void popupThreeLangNational() {
        user.setsLanguage(HeaderData.THIRD_LANG);
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherExtPopUp);
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcherExtPopUp.nationalLang,
                HeaderData.NATIONAL_LANG_LINK, HEADER);
        user.clicksOn(mainPage.headerBlock.langSwitcherExtPopUp.nationalLang);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcher, HeaderData.NATIONAL_LANG_CODE);
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcherPopUp.currentLang,
                equalToIgnoringCase(HeaderData.NATIONAL_LANG_CODE));
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcherPopUp.secondLang,
                HeaderData.DEFAULT_LANG_LINK, HEADER);
    }

    @Test
    public void popupThreeLangThird() {
        user.setsLanguage(HeaderData.THIRD_LANG);
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherExtPopUp);
        user.shouldSeeElementWithText(mainPage.headerBlock.langSwitcherExtPopUp.currentLang,
                equalToIgnoringCase(HeaderData.THIRD_LANG_CODE));
    }


    @Test
    public void popupThreeMoreLangLink() {
        user.setsLanguage(HeaderData.THIRD_LANG);
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherExtPopUp);
        userLink.shouldSeeLink(mainPage.headerBlock.langSwitcherExtPopUp.more,
                HeaderData.THREE_MORE_LANG_LINK, HEADER);
    }

    @Test
    @Ignore
    public void syncWithPassport() throws IOException, ParserConfigurationException, SAXException {
        User login = mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode());
        user.logsInAs(login, CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.setsLanguage(Language.EN);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcher);
        user.clicksOn(mainPage.headerBlock.langSwitcher);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp);
        user.shouldSeeElement(mainPage.headerBlock.langSwitcherPopUp.secondLang);
        user.clicksOn(mainPage.headerBlock.langSwitcherPopUp.secondLang);
        user.shouldNotSeeElement(mainPage.headerBlock.langSwitcherPopUp);
        userHeader.shouldSeePassportLang(HeaderData.NATIONAL_LANG, login);
    }

}
