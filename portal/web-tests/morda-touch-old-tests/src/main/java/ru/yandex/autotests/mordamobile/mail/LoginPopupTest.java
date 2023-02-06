package ru.yandex.autotests.mordamobile.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordamobile.data.MailData.*;
import static ru.yandex.autotests.utils.morda.auth.User.NEW_DEFAULT;

/**
 * User: ivannik
 * Date: 05.03.14
 * Time: 13:41
 */
@Aqua.Test(title = "Авторизационный почтовый домик")
@Features("Mail")
@Stories("Authorisation")
public class LoginPopupTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule(DesiredCapabilities.chrome());

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.mailBlock);
        user.clicksOn(homePage.mailBlock);
        user.shouldSeeElement(homePage.loginPopup);
    }

    @Test
    public void titleExist() {
        user.shouldSeeElementWithText(homePage.loginPopup.title, DOMIK_TITLE_MATCHER);
    }

    @Test
    public void loginPopupCanBeClosed() {
        user.shouldSeeElement(homePage.loginPopup.closeCross);
        user.clicksOn(homePage.loginPopup.closeCross);
        user.shouldNotSeeElement(homePage.loginPopup);
    }

    @Test
    public void loginInputExistAndErasable() {
        user.shouldNotSeeElement(homePage.loginPopup.clearLoginCross);
        user.shouldSeeElement(homePage.loginPopup.loginInput);
        user.entersTextInInput(homePage.loginPopup.loginInput, NEW_DEFAULT.getLogin());
        user.shouldSeeInputWithText(homePage.loginPopup.loginInput, NEW_DEFAULT.getLogin());
        user.shouldSeeElement(homePage.loginPopup.clearLoginCross);
        user.clicksOn(homePage.loginPopup.clearLoginCross);
        user.shouldSeeInputWithText(homePage.loginPopup.loginInput, EMPTY_STRING);
    }

    @Test
    public void passwordInputExistAndErasable() {
        user.shouldNotSeeElement(homePage.loginPopup.clearPasswordCross);
        user.shouldSeeElement(homePage.loginPopup.passwordInput);
        user.entersTextInInput(homePage.loginPopup.passwordInput, NEW_DEFAULT.getPassword());
        user.shouldSeeInputWithText(homePage.loginPopup.passwordInput, NEW_DEFAULT.getPassword());
        user.shouldSeeElement(homePage.loginPopup.clearPasswordCross);
        user.clicksOn(homePage.loginPopup.clearPasswordCross);
        user.shouldSeeInputWithText(homePage.loginPopup.passwordInput, EMPTY_STRING);
    }

    @Test
    public void remindPasswordButton() {
        user.shouldSeeElement(homePage.loginPopup.remindPasswordButton);
        user.shouldSeeLink(homePage.loginPopup.remindPasswordButton, REMIND_PASSWORD_LINK);
    }

    @Test
    public void registerButton() {
        user.shouldSeeElement(homePage.loginPopup.registrationButton);
        user.shouldSeeLink(homePage.loginPopup.registrationButton, REGISTER_LINK);
    }

    @Test
    public void canLogin() {
        user.shouldSeeElement(homePage.loginPopup.loginInput);
        user.entersTextInInput(homePage.loginPopup.loginInput, NEW_DEFAULT.getLogin());
        user.shouldSeeElement(homePage.loginPopup.passwordInput);
        user.entersTextInInput(homePage.loginPopup.passwordInput, NEW_DEFAULT.getPassword());
        user.clicksOn(homePage.loginPopup.authButton);
        user.shouldSeePage(LOGGED_MAIL_URL);
    }

    @Test
    public void socialAuthButtonsExists() {
        user.shouldSeeElement(homePage.loginPopup.ggLoginButton);
        user.shouldSeeElement(homePage.loginPopup.vkLoginButton);
        user.shouldSeeElement(homePage.loginPopup.mrLoginButton);
        user.shouldSeeElement(homePage.loginPopup.twLoginButton);
        user.shouldSeeElement(homePage.loginPopup.fbLoginButton);
        user.shouldSeeElement(homePage.loginPopup.okLoginButton);
    }
}
