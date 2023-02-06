package ru.yandex.autotests.mainmorda.commontests.skins;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.SkinsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.SkinsData.*;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;

/**
 * User: alex89
 * Date: 01.08.12
 * Проверка кнопок, ссылок меню в 4-х разных ситуациях
 */
@Aqua.Test(title = "Проверка меню")
@Features({"Main", "Common", "Skins"})
@Stories("Menu")
public class SkinsMenuTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        userSkins.opensThemeMenu();
    }

    @Test
    public void skinsMenuWithoutSelectedSkin() {
        user.shouldSeeElement(mainPage.themeMenu.closeCross);
        user.shouldSeeElementWithText(mainPage.themeMenu.closeCross, CLOSE_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.closeCross,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldSeeElement(mainPage.themeMenu.cancelButton);
        user.shouldSeeElementWithText(mainPage.themeMenu.cancelButton, CANCEL_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.cancelButton,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldNotSeeElement(mainPage.themeMenu.saveThemeButton);
        user.shouldNotSeeElement(mainPage.themeMenu.resetThemeLink);

        user.clicksOn(mainPage.themeMenu.closeCross);
        user.shouldNotSeeElement(mainPage.themeMenu);
    }

    @Test
    public void skinsMenuWithSelectedSkin() {
        userSkins.setSkinWithUrl(RANDOM_SKIN);

        user.shouldSeeElement(mainPage.themeMenu.closeCross);
        user.shouldSeeElementWithText(mainPage.themeMenu.closeCross, CLOSE_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.closeCross,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldSeeElement(mainPage.themeMenu.cancelButton);
        user.shouldSeeElementWithText(mainPage.themeMenu.cancelButton, CANCEL_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.cancelButton,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldSeeElement(mainPage.themeMenu.saveThemeButton);
        user.shouldSeeElementWithText(mainPage.themeMenu.saveThemeButton, SAVE_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.saveThemeButton,
                hasAttribute(HREF, getButtonHrefMatcher(RANDOM_SKIN, CookieManager.getSecretKey(driver))));

        user.shouldNotSeeElement(mainPage.themeMenu.resetThemeLink);

        user.clicksOn(mainPage.themeMenu.closeCross);
        user.shouldNotSeeElement(mainPage.themeMenu);
    }

    @Test
    public void skinsMenuAfterSavingSkin() {
        userSkins.savesSkinWithUrl(RANDOM_SKIN);
        userSkins.opensThemeMenu();

        user.shouldSeeElement(mainPage.themeMenu.closeCross);
        user.shouldSeeElementWithText(mainPage.themeMenu.closeCross, CLOSE_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.closeCross,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldSeeElement(mainPage.themeMenu.cancelButton);
        user.shouldSeeElementWithText(mainPage.themeMenu.cancelButton, CANCEL_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.cancelButton,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldSeeElement(mainPage.themeMenu.resetThemeLink);
        user.shouldSeeElementWithText(mainPage.themeMenu.resetThemeLink, RESET_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.resetThemeLink,
                hasAttribute(HREF, getButtonHrefMatcher(DEFAULT_SKIN_ID, CookieManager.getSecretKey(driver))));

        user.shouldNotSeeElement(mainPage.themeMenu.saveThemeButton);

        user.clicksOn(mainPage.themeMenu.closeCross);
        user.shouldNotSeeElement(mainPage.themeMenu);
    }

    @Test
    public void skinsMenuAfterSavingSkinAndChoosingAnotherSkin() {
        userSkins.savesSkinWithUrl(RANDOM_SKIN);
        userSkins.opensThemeMenu();
        userSkins.setSkinWithUrl(RANDOM_SKIN_2);

        user.shouldSeeElement(mainPage.themeMenu.closeCross);
        user.shouldSeeElementWithText(mainPage.themeMenu.closeCross, CLOSE_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.closeCross,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldSeeElement(mainPage.themeMenu.cancelButton);
        user.shouldSeeElementWithText(mainPage.themeMenu.cancelButton, CANCEL_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.cancelButton,
                hasAttribute(HREF, DEFAULT_BUTTON_HREF_MATCHER));

        user.shouldSeeElement(mainPage.themeMenu.saveThemeButton);
        user.shouldSeeElementWithText(mainPage.themeMenu.saveThemeButton, SAVE_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.saveThemeButton,
                hasAttribute(HREF, getButtonHrefMatcher(RANDOM_SKIN_2, CookieManager.getSecretKey(driver))));

        user.shouldSeeElement(mainPage.themeMenu.resetThemeLink);
        user.shouldSeeElementWithText(mainPage.themeMenu.resetThemeLink, RESET_BUTTON_TEXT_MATCHER);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.resetThemeLink,
                hasAttribute(HREF, getButtonHrefMatcher(DEFAULT_SKIN_ID, CookieManager.getSecretKey(driver))));

        user.clicksOn(mainPage.themeMenu.closeCross);
        user.shouldNotSeeElement(mainPage.themeMenu);
    }
}