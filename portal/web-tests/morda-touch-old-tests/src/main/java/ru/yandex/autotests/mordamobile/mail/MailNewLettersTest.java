package ru.yandex.autotests.mordamobile.mail;


import org.hamcrest.Matcher;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.utils.morda.auth.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Arrays;
import java.util.Collection;

import static ru.yandex.autotests.mordamobile.data.MailData.FIVE_LETTERS_TEXT;
import static ru.yandex.autotests.mordamobile.data.MailData.MAIL_EMPTY_TEXT;
import static ru.yandex.autotests.mordamobile.data.MailData.ONE_LETTER_TEXT;
import static ru.yandex.autotests.mordamobile.data.MailData.TWO_LETTERS_TEXT;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_FIVE_LETTERS;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_NO_LETTERS;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_ONE_LETTER;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_TWO_LETTERS;

/**
 * User: alex89
 * Date: 15.05.12
 * Часть тестирования несвёрнутого залогиненного почтового домика
 * Тестируется только текст о новых письмах.  писем нет, 1 , 2, 5 новых писем
 */
@Aqua.Test(title = "Сообщение о новых письмах")
@RunWith(Parameterized.class)
@Features("Mail")
@Stories("Count")
public class MailNewLettersTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> data() {
        return Arrays.asList(
                new Object[]{TURKEY_NO_LETTERS, MAIL_EMPTY_TEXT},
                new Object[]{TURKEY_ONE_LETTER, ONE_LETTER_TEXT},
                new Object[]{TURKEY_TWO_LETTERS, TWO_LETTERS_TEXT},
                new Object[]{TURKEY_FIVE_LETTERS, FIVE_LETTERS_TEXT}
        );
    }

    private User login;
    private Matcher<String> lettersMatcher;

    public MailNewLettersTest(User login, Matcher<String> lettersMatcher) {
        this.login = login;
        this.lettersMatcher = lettersMatcher;
    }

    @Test
    public void lettersText() {
        user.logsInAs(login, CONFIG.getBaseURL());
        user.setsLanguage(CONFIG.getLang());
        user.shouldSeeElement(homePage.mailBlock);
        user.shouldSeeElement(homePage.mailBlock.letterText);
        user.shouldSeeElementWithText(homePage.mailBlock.letterText, lettersMatcher);
    }
}

