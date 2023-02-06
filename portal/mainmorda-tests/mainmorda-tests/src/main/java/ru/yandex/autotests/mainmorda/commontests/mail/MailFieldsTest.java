package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.MailData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.MailData.PASSWORD_TEXT;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.PLACEHOLDER;


/**
 * User: alex89
 * Date: 09.10.12
 */
@Aqua.Test(title = "Поля логин и пароль незалогинового домика")
@Features({"Main", "Common", "Mail"})
@Stories("Login Fields")
public class MailFieldsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode());
        user.shouldSeeElement(mainPage.mailBlock);
    }

    @Test
    public void defaultLoginText() {
        user.shouldSeeElement(mainPage.mailBlock.loginInput);
        user.shouldSeeElementMatchingTo(mainPage.mailBlock.loginInput, hasAttribute(PLACEHOLDER, MailData.LOGIN_TEXT));
    }

    @Test
    public void defaultPasswordText() {
        user.shouldSeeElement(mainPage.mailBlock.passwordInput);
        user.shouldSeeElementMatchingTo(mainPage.mailBlock.passwordInput, hasAttribute(PLACEHOLDER, PASSWORD_TEXT));
    }
}
