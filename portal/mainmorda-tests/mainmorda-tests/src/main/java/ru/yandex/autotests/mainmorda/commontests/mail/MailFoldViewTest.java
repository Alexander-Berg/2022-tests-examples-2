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
import static ru.yandex.autotests.mainmorda.data.MailData.ICON_MATCHER;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_OVER_ENTER_LINK;


/**
 * User: alex89
 * Date: 11.05.12
 * Тестирование внешнего вида почтового домика
 */
@Aqua.Test(title = "Незалогиновый свернутый домик")
@Features({"Main", "Common", "Mail"})
@Stories("Fold View")
public class MailFoldViewTest {
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
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode());

        user.shouldSeeElement(mainPage.mailBlock);
        user.shouldSeeElement(mainPage.mailBlock.foldButton);
        user.clicksOn(mainPage.mailBlock.foldButton);
        user.shouldSeeElement(mainPage.mailFoldBlock);
    }

    @Test
    public void expandLinkInFoldMode() {
        user.shouldSeeElement(mainPage.mailFoldBlock.expandIcon);
        user.shouldSeeElementMatchingTo(mainPage.mailFoldBlock.expandIcon, ICON_MATCHER);
        user.shouldSeeElement(mainPage.mailFoldBlock.expandButton);
        user.clicksOn(mainPage.mailFoldBlock.expandButton);
        user.shouldSeeElement(mainPage.mailBlock);
    }

    @Test
    public void enterLinkInFoldMode() {
        userLink.shouldSeeLink(mainPage.mailFoldBlock.loginLink, MAIL_OVER_ENTER_LINK, MAIL);
    }
}
