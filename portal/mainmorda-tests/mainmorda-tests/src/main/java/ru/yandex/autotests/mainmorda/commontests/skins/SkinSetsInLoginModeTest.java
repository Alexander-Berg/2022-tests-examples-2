package ru.yandex.autotests.mainmorda.commontests.skins;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.SkinsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.SkinsData.RANDOM_SKIN;
import static ru.yandex.autotests.mainmorda.data.SkinsData.RANDOM_SKIN_2;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 24.01.13
 * <p/>
 * 1)Ставим скин в залогиненном режиме и проверяем,
 * что для залогинового пользователя скин выставился,
 * а для незалогинового отображается стандартный дизайн
 * 2) Ставим скин один скин для незалогинового пользователя и другой для залогинового
 * и проверяем,что они затем сохраняются и отображаются корректно
 */

@Aqua.Test(title = "Установка скина в залогиненном режиме")
@Features({"Main", "Common", "Skins"})
@Stories("Set Skin")
public class SkinSetsInLoginModeTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private User login;

    @Before
    public void setUp() {
        login = mordaAllureBaseRule.getUser(DEFAULT, CONFIG.getMode());
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.logsInAs(login, CONFIG.getBaseURL());
        userMode.setModeLogged(CONFIG.getMode());
    }

    @Test
    public void skinSavesForAuthorisedUser() {
        userSkins.savesSkinWithUrl(RANDOM_SKIN);
        userSkins.shouldSeeSkin(RANDOM_SKIN);
        user.logsOut();
        userSkins.shouldSeeDefaultMordaDesign();
        user.logsInAs(login, CONFIG.getBaseURL());
        userSkins.shouldSeeSkin(RANDOM_SKIN);
    }

    @Test
    public void skinSavesForAuthorisedAndUnauthorisedUser() {
        userSkins.savesSkinWithUrl(RANDOM_SKIN);
        userSkins.shouldSeeSkin(RANDOM_SKIN);
        user.logsOut();
        userSkins.savesSkinWithUrl(RANDOM_SKIN_2);
        userSkins.shouldSeeSkin(RANDOM_SKIN_2);
        user.logsInAs(login, CONFIG.getBaseURL());
        userSkins.shouldSeeSkin(RANDOM_SKIN);
        user.logsOut();
        userSkins.shouldSeeSkin(RANDOM_SKIN_2);
    }
}