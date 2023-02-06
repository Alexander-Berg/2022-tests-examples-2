package ru.yandex.autotests.mordamobile.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordamobile.data.MailData.LOGIN_TEXT;
import static ru.yandex.autotests.mordamobile.data.MailData.MAIL_LINK;
import static ru.yandex.autotests.mordamobile.data.MailData.TITLE;


/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Информер почты")
@Features("Mail")
@Stories("Appearance")
public class MailTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.mailBlock);
    }

    @Test
    public void mailTitle() {
        user.shouldSeeElement(homePage.mailBlock.title);
        user.shouldSeeElementWithText(homePage.mailBlock.title, TITLE);
    }

    @Test
    public void mailIcon() {
        user.shouldSeeElement(homePage.mailBlock.icon);
    }

    @Test
    public void mailLink() {
        user.shouldSeeLinkLight(homePage.mailBlock.mailLink, MAIL_LINK);
        user.clicksOn(homePage.mailBlock.mailLink);
        user.shouldSeeElement(homePage.loginPopup);
    }

    @Test
    public void loginText() {
        user.shouldSeeElement(homePage.mailBlock.loginText);
        user.shouldSeeElementWithText(homePage.mailBlock.loginText,
                LOGIN_TEXT);
    }
}
