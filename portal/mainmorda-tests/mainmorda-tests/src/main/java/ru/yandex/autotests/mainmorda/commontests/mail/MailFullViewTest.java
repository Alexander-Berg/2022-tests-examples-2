package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.MailSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.blocks.PageBlock.MAIL;
import static ru.yandex.autotests.mainmorda.data.MailData.ALIEN_PC_CHECKBOX_TEXT;
import static ru.yandex.autotests.mainmorda.data.MailData.FILL_FIELD_ERROR;
import static ru.yandex.autotests.mainmorda.data.MailData.ICON_MATCHER;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_CREATE_ACCOUNT_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_ENTER_TEXT;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_REMIND_PASSWORD_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_TITLE_LINK;
import static ru.yandex.autotests.mainmorda.data.MailData.RANDOM_TEXT_EN;

/**
 * User: alex89
 * Date: 11.05.12
 * Тестирование внешнего вида почтового домика
 */
@Aqua.Test(title = "Незалогиновый домик")
@Features({"Main", "Common", "Mail"})
@Stories("Full View")
public class MailFullViewTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MailSteps userMail = new MailSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode());

        user.shouldSeeElement(mainPage.mailBlock);
    }

    @Test
    public void titleLink() {
        userLink.shouldSeeLink(mainPage.mailBlock.title, MAIL_TITLE_LINK, MAIL);
    }

    @Test
    public void alienPcCheckBox() {
        user.shouldSeeElementIsNotSelected(mainPage.mailBlock.alienPCCheckbox);
        user.selectElement(mainPage.mailBlock.alienPCCheckbox);
        user.shouldSeeElementIsSelected(mainPage.mailBlock.alienPCCheckbox);
        user.shouldSeeElement(mainPage.mailBlock.alienPCCheckboxText);
        user.shouldSeeElementWithText(mainPage.mailBlock.alienPCCheckboxText,
                ALIEN_PC_CHECKBOX_TEXT);
    }

    @Test
    public void createAccountButton() {
        user.shouldSeeLinkLight(mainPage.mailBlock.createAccountButton, MAIL_CREATE_ACCOUNT_LINK);
    }

    @Test
    public void loginButtonWithoutLoginAndPwd() {
        user.shouldSeeElement(mainPage.mailBlock.loginButtonText);
        user.shouldSeeElementWithText(mainPage.mailBlock.loginButtonText, MAIL_ENTER_TEXT);
        user.clicksOn(mainPage.mailBlock.loginButton);
        user.shouldSeeElement(mainPage.mailBlock.errorMessage);
        user.shouldSeeElementWithText(mainPage.mailBlock.errorMessage, FILL_FIELD_ERROR);
    }

    @Test
    public void loginButtonWithoutLogin() {
        user.entersTextInInput(mainPage.mailBlock.passwordInput, RANDOM_TEXT_EN);
        user.clicksOn(mainPage.mailBlock.loginButton);
        user.shouldSeeElement(mainPage.mailBlock.errorMessage);
        user.shouldSeeElementWithText(mainPage.mailBlock.errorMessage, FILL_FIELD_ERROR);
    }

    @Test
    public void loginButtonWithoutPwd() {
        user.entersTextInInput(mainPage.mailBlock.loginInput, RANDOM_TEXT_EN);
        user.clicksOn(mainPage.mailBlock.loginButton);
        user.shouldSeeElement(mainPage.mailBlock.errorMessage);
        user.shouldSeeElementWithText(mainPage.mailBlock.errorMessage, FILL_FIELD_ERROR);
    }

    @Test
    public void remindPasswordLink() {
        userLink.shouldSeeLink(mainPage.mailBlock.remindPwd, MAIL_REMIND_PASSWORD_LINK, MAIL);
    }

    @Test
    public void mailFoldLink() {
        user.shouldSeeElement(mainPage.mailBlock.foldIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailBlock.foldIcon, ICON_MATCHER);
        user.shouldSeeElement(mainPage.mailBlock.foldButton);
        user.clicksOn(mainPage.mailBlock.foldButton);
        user.shouldSeeElement(mainPage.mailFoldBlock);
    }
}