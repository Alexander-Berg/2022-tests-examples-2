package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.MailSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_DOMIK;

/**
 * User: alex89
 * Date: 09.10.12
 */

@Aqua.Test(title = "Залогинивание в почту")
@Features({"Main", "Common", "Mail"})
@Stories("Login")
public class MailLoginTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MailSteps userMail = new MailSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode());
        user.shouldSeeElement(mainPage.mailBlock);
        user.entersTextInInput(mainPage.mailBlock.loginInput, TURKEY_DOMIK.getLogin());
        user.entersTextInInput(mainPage.mailBlock.passwordInput, TURKEY_DOMIK.getPassword());
    }

    @Test
    public void loginToMail() {
        user.clicksOn(mainPage.mailBlock.loginButton);
        userMail.shouldSeeLoggedMailPageWithHttps();
    }

    @Test
    public void loginToMailFromAlienPC() {
        user.clicksOn(mainPage.mailBlock.alienPCCheckbox);
        user.clicksOn(mainPage.mailBlock.loginButton);
        userMail.shouldSeeLoggedMailPageWithHttps();
    }
}
