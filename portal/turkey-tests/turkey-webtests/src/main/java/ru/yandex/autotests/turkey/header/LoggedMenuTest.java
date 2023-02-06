package ru.yandex.autotests.turkey.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.turkey.data.HeaderData.LOGOUT_LINK;
import static ru.yandex.autotests.turkey.data.HeaderData.PASSPORT_LINK;
import static ru.yandex.autotests.turkey.data.HeaderData.REGION_LINK;
import static ru.yandex.autotests.turkey.data.HeaderData.SETTINGS_LINK;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_HEADER;

/**
 * User: ivannik
 * Date: 13.06.13
 * Time: 14:25
 */
@Aqua.Test(title = "Выпадающая вкладка под именем логина")
@Features("Header")
@Stories("Logged Menu")
public class LoggedMenuTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.logsInAs(TURKEY_HEADER, CONFIG.getBaseURL());
        user.shouldSeeElement(yandexComTrPage.headerBlock.loginNameButton);
        user.clicksOn(yandexComTrPage.headerBlock.loginNameButton);
        user.shouldSeeElement(yandexComTrPage.headerBlock.loggedPopUp);
    }

    @Test
    public void loginButtonText() {
        user.shouldSeeElementWithText(yandexComTrPage.headerBlock.loginNameButton, TURKEY_HEADER.getLogin());
    }

    @Test
    public void settingsLink() {
        user.shouldSeeLink(yandexComTrPage.headerBlock.loggedPopUp.settingsLink, SETTINGS_LINK);
    }

    @Test
    public void regionLink() {
        user.shouldSeeLink(yandexComTrPage.headerBlock.loggedPopUp.regionLink, REGION_LINK);
    }

    @Test
    public void passportLink() {
        user.shouldSeeLink(yandexComTrPage.headerBlock.loggedPopUp.passportLink, PASSPORT_LINK);
    }

    @Test
    public void logoutLink() {
        user.shouldSeeLink(yandexComTrPage.headerBlock.loggedPopUp.logoutLink, LOGOUT_LINK);
    }
}
