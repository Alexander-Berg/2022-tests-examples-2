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
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.SkinsData.DEFAULT_SKIN_ID;
import static ru.yandex.autotests.mainmorda.data.SkinsData.RANDOM_SKIN_ID;

/**
 * User: alex89
 * Date: 19.10.12
 */
@Aqua.Test(title = "Проверка иконок скинов 'Обычный Яндекс','Случайная тема'")
@Features({"Main", "Common", "Skins"})
@Stories("Icons")
public class SpecialSkinsIconsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void defaultSkin() {
        userSkins.opensThemeMenu();
        userSkins.shouldSeeSkinInMenuWhenChosen(DEFAULT_SKIN_ID);
        userSkins.setSkinWithClick(RANDOM_SKIN_ID);
        userSkins.shouldSeeSkinInMenuWhenNotChosen(DEFAULT_SKIN_ID);
    }

    @Test
    public void randomSkin() {
        userSkins.opensThemeMenu();
        userSkins.shouldSeeSkinInMenuWhenNotChosen(RANDOM_SKIN_ID);
        userSkins.setSkinWithClick(RANDOM_SKIN_ID);
        userSkins.shouldSeeSkinInMenuWhenChosen(RANDOM_SKIN_ID);
    }
}