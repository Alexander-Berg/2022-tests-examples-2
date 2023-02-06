package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Before;
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
import static ru.yandex.autotests.mainmorda.data.MailData.EXPAND_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.ICON_MATCHER;
import static ru.yandex.autotests.mainmorda.data.MailData.LETTER_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_COMPOSE_FOLD_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_TITLE_LOGGED_LINK;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 09.10.12
 */
@Aqua.Test(title = "Свёрнутый залогиновый домик")
@Features({"Main", "Common", "Mail"})
@Stories("Fold View")
public class MailFoldViewLoggedTest {
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
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.setsLanguage(CONFIG.getLang());

        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.shouldSeeElement(mainPage.mailLoggedBlock.foldIcon);
        user.clicksOn(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock);
    }

    @Test
    public void titleLinkInFoldModeLogged() {
        userLink.shouldSeeLink(mainPage.mailLoggedFoldBlock.title,
                MAIL_TITLE_LOGGED_LINK, MAIL);
    }

    @Test
    public void composeLinkInFoldModeLogged() {
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock.composeIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailLoggedFoldBlock.composeIcon, ICON_MATCHER);
        userLink.shouldSeeLink(mainPage.mailLoggedFoldBlock.composeText, MAIL_COMPOSE_FOLD_LINK, MAIL);
    }

    @Test
    public void letterLinkInFoldModeLogged() {
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock.letterIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailLoggedFoldBlock.letterIcon, ICON_MATCHER);
        userLink.shouldSeeLink(mainPage.mailLoggedFoldBlock.letterText, LETTER_LINK, MAIL);
    }

    @Test
    public void expandLinkInFoldModeLogged() {
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock.expandIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailLoggedFoldBlock.expandIcon, ICON_MATCHER);
        userLink.shouldSeeLink(mainPage.mailLoggedFoldBlock.expandButton, EXPAND_LINK, MAIL);
        user.clicksOn(mainPage.mailLoggedFoldBlock.expandButton);
        user.shouldSeeElement(mainPage.mailLoggedBlock);
    }

    @Test
    public void expandAndFoldActionsLogged() {
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock.expandButton);
        user.clicksOn(mainPage.mailLoggedFoldBlock.expandButton);

        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.shouldSeeElement(mainPage.mailLoggedBlock.foldIcon);
        user.clicksOn(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock.expandButton);
        user.clicksOn(mainPage.mailLoggedFoldBlock.expandButton);

        user.shouldSeeElement(mainPage.mailLoggedBlock);
    }
}