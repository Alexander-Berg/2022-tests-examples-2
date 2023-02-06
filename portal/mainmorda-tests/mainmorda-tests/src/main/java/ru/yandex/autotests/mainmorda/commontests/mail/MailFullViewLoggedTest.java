package ru.yandex.autotests.mainmorda.commontests.mail;

/**
 * User: alex89
 * Date: 09.10.12
 * todo:
 */

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
import static ru.yandex.autotests.mainmorda.data.MailData.ICON_MATCHER;
import static ru.yandex.autotests.mainmorda.data.MailData.LETTER_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_COMPOSE_FULL_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_TITLE_LOGGED_LINK;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 15.05.12
 * Тестирование несвёрнутого залогиненного почтового домика
 * Не тестируется только текст о новых письмах. Он тестируется в   MailNewLettersTest
 */
@Aqua.Test(title = "Несвёрнутый залогиновый домик")
@Features({"Main", "Common", "Mail"})
@Stories("Full View")
public class MailFullViewLoggedTest {
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
    }

    @Test
    public void titleLinkInFullMode() {
        userLink.shouldSeeLink(mainPage.mailLoggedBlock.title, MAIL_TITLE_LOGGED_LINK, MAIL);
    }

    @Test
    public void composeLinkInFullMode() {
        user.shouldSeeElement(mainPage.mailLoggedBlock.composeIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailLoggedBlock.composeIcon, ICON_MATCHER);
        userLink.shouldSeeLink(mainPage.mailLoggedBlock.composeText, MAIL_COMPOSE_FULL_LINK, MAIL);
    }

    @Test
    public void letterLinkInFullMode() {
        user.shouldSeeElement(mainPage.mailLoggedBlock.letterIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailLoggedBlock.letterIcon, ICON_MATCHER);
        userLink.shouldSeeLink(mainPage.mailLoggedBlock.letterText, LETTER_LINK, MAIL);
    }

    @Test
    public void foldLinkInFullMode() {
        user.shouldSeeElement(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailLoggedBlock.foldIcon, ICON_MATCHER);
        user.clicksOn(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock);
    }
}
