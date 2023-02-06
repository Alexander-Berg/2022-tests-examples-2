package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;
import ru.yandex.qatools.allure.annotations.Features;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 15.12.2014.
 */

@Aqua.Test(title = "Проверка мультиавторизации")
@Features({"Main", "Common", "Mail"})
public class MailMultiAuthorizationTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private final User baseUser = mordaAllureBaseRule.getUser(UserType.DEFAULT, Mode.PLAIN);
    private final User secondUser = mordaAllureBaseRule.getUser(UserType.DEFAULT, Mode.PLAIN);

    @Before
    public void setUp(){
        user.opensPage(CONFIG.getBaseURL());
    }

    @Test
    public void hasPromoTest() {
        user.logsInAs(baseUser,CONFIG.getBaseURL());
        user.logsOut(CONFIG.getBaseURL());
        user.shouldSeePage(CONFIG.getBaseURL());
        user.logsInAs(secondUser, CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp.multiAuthorizationBlock.promoWindow);
        user.refreshPage();
        user.shouldSeePage(CONFIG.getBaseURL());
        user.shouldNotSeeElement(mainPage.headerBlock.loginPopUp.multiAuthorizationBlock.promoWindow);
    }

    @Test
    public void openSettingsTest() {
        user.logsInAs(baseUser,CONFIG.getBaseURL());
        user.logsInAs(secondUser, CONFIG.getBaseURL());
        user.clicksOn(mainPage.headerBlock.loginNameLink);
        user.clicksOn(mainPage.headerBlock.loginPopUp.multiAuthorizationBlock.editListLink);
        user.shouldSeePage("https://passport.yandex.ru/");
    }

    @Test
    public void logOutTest() {
        user.logsInAs(baseUser,CONFIG.getBaseURL());
        user.logsInAs(secondUser, CONFIG.getBaseURL());
        user.clicksOn(mainPage.headerBlock.loginNameLink);
        user.clicksOn(mainPage.headerBlock.loginPopUp.multiAuthorizationBlock.exitLink);
        user.shouldSeeElement(mainPage.mailBlock);
    }

    @Test
    public void addUserTest() {
        user.logsInAs(mordaAllureBaseRule.getUser(UserType.DEFAULT, Mode.PLAIN),CONFIG.getBaseURL());
        user.clicksOn(mainPage.headerBlock.loginNameLink);
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp);
        user.clicksOn(mainPage.headerBlock.loginPopUp.multiAuthorizationBlock.addUserLink);
        user.shouldSeePage("https://passport.yandex.ru/");
    }

    @Test
    public void switchUserTest() {
        for(int i = 0; i != 5; i++) {
            User u = mordaAllureBaseRule.getUser(UserType.DEFAULT, Mode.PLAIN);
            user.logsInAs(u, CONFIG.getBaseURL());
       }
       user.clicksOn(mainPage.headerBlock.loginNameLink);
       String name =  mainPage.headerBlock.loginPopUp.multiAuthorizationBlock.firstUser.getText();
       user.clicksOn(mainPage.headerBlock.loginPopUp.multiAuthorizationBlock.firstUser);
       user.shouldSeeElementWithText(mainPage.headerBlock.loginNameLink, name);
    }
}
