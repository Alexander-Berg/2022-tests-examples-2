package ru.yandex.autotests.mainmorda.commontests.secretkey;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.SkinsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.SkinsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.SkinsData.RANDOM_SKIN;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 10.06.12
 */
@Aqua.Test(title = "Установка темы с рандомным SK")
@Features({"Main", "Common", "Skins"})
@Stories("Secret Key")
public class CantSetThemeWithRandomSKTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private SkinsSteps userSkin = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
    }

    @Test
    public void setThemeWithRandomSKLogoff() {
        userMode.setMode(CONFIG.getMode());
        userSkin.savesSkinWithUrlWithRandomSK(RANDOM_SKIN);
        user.shouldSeePage(SkinsData.THEME_PAGE_URL);
        userSkin.shouldSeeSkin(RANDOM_SKIN);
    }

    @Test
    public void setThemeWithRandomSKLogin() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode()),
                CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
        userSkin.savesSkinWithUrlWithRandomSK(RANDOM_SKIN);
        user.shouldSeePage(SkinsData.THEME_PAGE_URL);
        userSkin.shouldSeeSkin(RANDOM_SKIN);
    }
}
