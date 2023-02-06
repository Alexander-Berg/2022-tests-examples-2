package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.blocks.PageBlock.MAIL;
import static ru.yandex.autotests.mainmorda.data.MailData.getExitLink;
import static ru.yandex.autotests.utils.morda.cookie.CookieManager.getYandexUid;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 09.10.12
 * Проверка работы ссылки "Выход" из почты.
 */

@Aqua.Test(title = "Ссылка 'Выход' из почты")
@Features({"Main", "Common", "Mail"})
@Stories("Exit Link")
public class MailExitLinkTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Test
    public void exitLinkWithFullLoggedMailBlock() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode()),
                CONFIG.getBaseURL());
        user.setsLanguage(CONFIG.getLang());
        userMode.setModeLogged(CONFIG.getMode());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.shouldSeeElement(mainPage.headerBlock.loginNameLink);
        user.clicksOn(mainPage.headerBlock.loginNameLink);
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp);
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp.exitLink);
        userLink.shouldSeeLink(mainPage.headerBlock.loginPopUp.exitLink,
                getExitLink(getYandexUid(driver)), MAIL);
        user.clicksOn(mainPage.headerBlock.loginPopUp.exitLink);
        user.shouldSeeElement(mainPage.mailBlock);
    }

    @Test
    public void exitLinkWithFoldLoggedMailBlock() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode()),
                CONFIG.getBaseURL());
        user.setsLanguage(CONFIG.getLang());
        userMode.setModeLogged(CONFIG.getMode());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.clicksOn(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock);
        user.shouldSeeElement(mainPage.headerBlock.loginNameLink);
        user.clicksOn(mainPage.headerBlock.loginNameLink);
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp);
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp.exitLink);
        userLink.shouldSeeLink(mainPage.headerBlock.loginPopUp.exitLink,
                getExitLink(getYandexUid(driver)), MAIL);
        user.clicksOn(mainPage.headerBlock.loginPopUp.exitLink);
        user.shouldSeeElement(mainPage.mailBlock);
    }

    @Test
    public void exitLinkWithNoMailAccount() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode()),
                CONFIG.getBaseURL());
        user.setsLanguage(CONFIG.getLang());
        userMode.setModeLogged(CONFIG.getMode());
        user.shouldSeeElement(mainPage.headerBlock.loginNameLink);
        user.clicksOn(mainPage.headerBlock.loginNameLink);
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp);
        user.shouldSeeElement(mainPage.headerBlock.loginPopUp.exitLink);
        userLink.shouldSeeLink(mainPage.headerBlock.loginPopUp.exitLink,
                getExitLink(getYandexUid(driver)), MAIL);
        user.clicksOn(mainPage.headerBlock.loginPopUp.exitLink);
        user.shouldSeeElement(mainPage.mailBlock);

    }
}
