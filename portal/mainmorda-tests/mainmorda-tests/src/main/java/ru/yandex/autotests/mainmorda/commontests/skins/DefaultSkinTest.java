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
import static ru.yandex.autotests.mainmorda.data.SkinsData.RANDOM_SKIN;

/**
 * User: alex89
 * Date: 01.08.12
 */
@Aqua.Test(title = "Проверка выставления скина 'Обычный Яндекс'")
@Features({"Main", "Common", "Skins"})
@Stories("Default Skin")
public class DefaultSkinTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() throws InterruptedException {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        userSkins.savesSkinWithUrl(RANDOM_SKIN);
        userSkins.shouldSeeSkin(RANDOM_SKIN);
        userSkins.opensThemeMenu();
        user.shouldSeeElement(mainPage.themeMenu.tabsListInMenu.get(0));
        user.clicksOn(mainPage.themeMenu.tabsListInMenu.get(0));
        Thread.sleep(1000);
    }

    @Test
    public void defaultSkinChoosesWhenRandomSkinChosen() {
        userSkins.setSkinWithClick(DEFAULT_SKIN_ID);
        userSkins.shouldSeeDefaultMordaDesign();
        user.refreshPage();
        userSkins.shouldSeeDefaultMordaDesign();
    }

    @Test
    public void defaultSkinSavesWhenRandomSkinChosen() {
        userSkins.setSkinWithClick(DEFAULT_SKIN_ID);
        userSkins.shouldSeeDefaultMordaDesign();
        user.shouldSeeElement(mainPage.themeMenu);
        user.shouldSeeElement(mainPage.themeMenu.saveThemeButton);
        user.clicksOn(mainPage.themeMenu.saveThemeButton);
        userSkins.shouldSeeDefaultMordaDesign();
        user.refreshPage();
        user.shouldNotSeeElement(mainPage.themeMenu);
        userSkins.shouldSeeDefaultMordaDesign();
    }
}