package ru.yandex.autotests.mainmorda.commontests.mail;


import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.MailData.FIVE_LETTERS_TEXT;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_EMPTY_TEXT;
import static ru.yandex.autotests.mainmorda.data.MailData.ONE_LETTER_FOLD_TEXT;
import static ru.yandex.autotests.mainmorda.data.MailData.ONE_LETTER_TEXT;
import static ru.yandex.autotests.mainmorda.data.MailData.TWO_LETTERS_TEXT;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_0;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_1;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_2;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_5;

/**
 * User: alex89
 * Date: 15.05.12
 * Часть тестирования несвёрнутого залогиненного почтового домика
 * Тестируется только текст о новых письмах.  писем нет, 1 , 2, 5 новых писем
 */
@Aqua.Test(title = "Сообщение о новых письмах")
@Features({"Main", "Common", "Mail"})
@Stories("New Letters")
public class MailNewLettersTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Test
    public void noLettersText() {
        user.logsInAs(mordaAllureBaseRule.getUser(MAIL_0, CONFIG.getMode()),
                CONFIG.getBaseURL());

        userMode.setModeLogged(CONFIG.getMode());
        user.setsLanguage(CONFIG.getLang());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.shouldSeeElement(mainPage.mailLoggedBlock.letterText);
        user.shouldSeeElementWithText(mainPage.mailLoggedBlock.letterText, MAIL_EMPTY_TEXT);
    }

    @Test
    public void oneLetterText() {
        user.logsInAs(mordaAllureBaseRule.getUser(MAIL_1, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.setsLanguage(CONFIG.getLang());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.shouldSeeElement(mainPage.mailLoggedBlock.letterText);
        user.shouldSeeElementWithText(mainPage.mailLoggedBlock.letterText, ONE_LETTER_TEXT);
    }

    @Test
    public void twoLettersText() {
        user.logsInAs(mordaAllureBaseRule.getUser(MAIL_2, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.setsLanguage(CONFIG.getLang());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.shouldSeeElement(mainPage.mailLoggedBlock.letterText);
        user.shouldSeeElementWithText(mainPage.mailLoggedBlock.letterText, TWO_LETTERS_TEXT);
    }

    @Test
    public void fiveLettersText() {
        user.logsInAs(mordaAllureBaseRule.getUser(MAIL_5, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.setsLanguage(CONFIG.getLang());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.shouldSeeElement(mainPage.mailLoggedBlock.letterText);
        user.shouldSeeElementWithText(mainPage.mailLoggedBlock.letterText, FIVE_LETTERS_TEXT);
    }

    @Test
    public void noLetterTextInFoldMode() {
        user.logsInAs(mordaAllureBaseRule.getUser(MAIL_0, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.setsLanguage(CONFIG.getLang());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.clicksOn(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock.letterText);
        user.shouldSeeElementWithText(mainPage.mailLoggedFoldBlock.letterText, MAIL_EMPTY_TEXT);
    }

    @Test
    public void oneLetterTextInFoldMode() {
        user.logsInAs(mordaAllureBaseRule.getUser(MAIL_1, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        user.clicksOn(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock);
        user.shouldSeeElementWithText(mainPage.mailLoggedFoldBlock.letterText,
                ONE_LETTER_FOLD_TEXT);
    }
}

