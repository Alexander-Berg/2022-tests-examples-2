package ru.yandex.autotests.mainmorda.commontests.header;

import org.junit.Before;
import org.junit.Ignore;
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
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.HEADER;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;
import static ru.yandex.autotests.utils.morda.users.UserType.LONG;

/**
 * User: eoff
 * Date: 18.01.13
 */
@Aqua.Test(title = "Проверка ссылки логина в хидере и попапа")
@Features({"Main", "Common", "Header"})
@Stories("Login Link")
public class HeaderLoginLinkTest {
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
        user.resizeWindow(1280, 1024);
    }

    @Test
    @Ignore
    public void loginButton() {
        userMode.setMode(CONFIG.getMode());
        user.shouldSeeElement(mainPage.headerBlock);
        userLink.shouldSeeLink(mainPage.headerBlock.loginButton, HeaderData.MAIL_LINK_LOGOFF, HEADER);
    }

    @Test
    @Ignore
    public void loginNameLink() {
        User login = mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode());
        user.logsInAs(login, CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.shouldSeeElement(mainPage.headerBlock.loginNameLink);
        user.shouldSeeElementWithText(mainPage.headerBlock.loginNameLink, equalTo(login.getLogin()));
    }

    @Test
    public void loginLongNameLink() {
        User login = mordaAllureBaseRule.getUser(LONG, CONFIG.getMode());
        user.logsInAs(login, CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.shouldSeeElement(mainPage.headerBlock.loginNameLink);
        user.shouldSeeElementWithText(mainPage.headerBlock.loginNameLink, login.getLogin().substring(0, 20) + "…");
    }

    @Test
    @Ignore
    public void loginNamePopupPassportLink() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.clicksOn(mainPage.headerBlock.loginNameLink);
        userLink.shouldSeeLink(mainPage.headerBlock.loginPopUp.passportLink,
                HeaderData.PASSPORT_LINK, HEADER);
    }
}
