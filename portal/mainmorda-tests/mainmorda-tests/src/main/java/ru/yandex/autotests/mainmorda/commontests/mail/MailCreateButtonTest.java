package ru.yandex.autotests.mainmorda.commontests.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.MailData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.utils.morda.users.UserType.NO_MAIL;

/**
 * User: alex89
 * Date: 09.10.12
 * Проверка кнопки "Завести почту"  для пользователя,
 * который создал свою учётную запись через паспорт,но не завёл почты.
 */

@Aqua.Test(title = "Кнопка 'завести почту'")
@Features({"Main", "Common", "Mail"})
@Stories("Create Button")
public class MailCreateButtonTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.logsInAs(mordaAllureBaseRule.getUser(NO_MAIL, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
    }

    @Test
    public void createMailButtonLink() {
        user.shouldSeeLinkLight(mainPage.overMailBlock.createMailButton,
                MailData.CREATE_MAIL_LINK);
    }

    @Test
    public void noMailBlocksWithCreateMailButton() {
        user.shouldNotSeeElement(mainPage.mailBlock);
        user.shouldNotSeeElement(mainPage.mailFoldBlock);
        user.shouldNotSeeElement(mainPage.mailLoggedBlock);
        user.shouldNotSeeElement(mainPage.mailLoggedFoldBlock);
    }
}
