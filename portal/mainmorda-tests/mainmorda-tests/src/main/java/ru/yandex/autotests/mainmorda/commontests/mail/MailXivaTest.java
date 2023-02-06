package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;

import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.mail.MailUtils;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.Matchers.equalToIgnoringCase;
import static org.hamcrest.Matchers.startsWith;


/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 12.12.2014.
 */

@Aqua.Test(title = "Проверка почтовой ксивы")
@Features({"Main", "Common", "Mail"})
public class MailXivaTest {

    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Test
    public void autoRefreshReceivedLettersForNotFoldedBlockTest() throws InterruptedException {
        User firstUser = mordaAllureBaseRule.getUser(UserType.DEFAULT, Mode.PLAIN);
        user.logsInAs(firstUser, CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.mailLoggedBlock);
        int numberOfLetters = getNumberOfLetters();
        sendMailTo(firstUser, "Bla bla bla");
        Thread.sleep(10000);
        user.shouldSeeElementWithText(mainPage.mailLoggedBlock.letterText,
                startsWith(String.valueOf(numberOfLetters + 1) + " "));
    }

    @Test
    public void autoRefreshReceivedLettersForFoldedBlockTest() throws InterruptedException {
        User firstUser = mordaAllureBaseRule.getUser(UserType.DEFAULT, Mode.PLAIN);
        user.logsInAs(firstUser, CONFIG.getBaseURL());
        user.clicksOn(mainPage.mailLoggedBlock.foldIcon);
        user.shouldSeeElement(mainPage.mailLoggedFoldBlock);
        int numberOfLetters = getNumberOfLettersFolded();
        sendMailTo(firstUser,"Bla bla bla");
        Thread.sleep(10000);
        user.shouldSeeElementWithText(mainPage.mailLoggedFoldBlock.letterText,
                equalToIgnoringCase(String.valueOf(numberOfLetters + 1)));
    }

    @Step("Send mail to {0} with subject {1}")
    public void sendMailTo(User u, String text) {
        MailUtils.mail().setTo(u.getLogin() + "@yandex.ru")
                .setFrom(u.getLogin() + "@yandex.ru")
                .setSubject("subject: " + text)
                .setText(text)
                .send();
    }

    private int getNumberOfLetters() {
        String text = mainPage.mailLoggedBlock.letterText.getText();
        return Integer.valueOf(text.substring(0, text.indexOf(' ')));
    }

    private int getNumberOfLettersFolded() {
        String text = mainPage.mailLoggedFoldBlock.letterText.getText();
        return Integer.valueOf(text);
    }
}
