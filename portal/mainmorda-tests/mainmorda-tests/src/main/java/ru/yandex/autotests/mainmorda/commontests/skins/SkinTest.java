package ru.yandex.autotests.mainmorda.commontests.skins;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.SkinsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.SkinsData.PARAMETRIZED_SKINS;

@Aqua.Test(title = "Установка скинов")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Skins"})
@Stories("Skin Actions")
public class SkinTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(PARAMETRIZED_SKINS);
    }

    private String skinId;

    public SkinTest(String skinId) {
        this.skinId = skinId;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        userSkins.resetSkins();
        userSkins.opensThemeMenu();
        userSkins.setSkinWithClick(skinId);
        userSkins.shouldSeeSkin(skinId);
    }

    @Test
    public void skinSave() {
        user.shouldSeeElement(mainPage.themeMenu.saveThemeButton);
        user.clicksOn(mainPage.themeMenu.saveThemeButton);
        user.shouldNotSeeElement(mainPage.themeMenu);
        userSkins.shouldSeeSkin(skinId);
        user.refreshPage();
        user.shouldNotSeeElement(mainPage.themeMenu);
        userSkins.shouldSeeSkin(skinId);
    }

    @Test
    public void skinCancel() {
        user.shouldSeeElement(mainPage.themeMenu.cancelButton);
        user.clicksOn(mainPage.themeMenu.cancelButton);
        user.shouldNotSeeElement(mainPage.themeMenu);
        userSkins.shouldSeeDefaultMordaDesign();
        user.refreshPage();
        user.shouldNotSeeElement(mainPage.themeMenu);
        userSkins.shouldSeeDefaultMordaDesign();
    }

    @Test
    public void skinReset() {
        user.shouldSeeElement(mainPage.themeMenu.saveThemeButton);
        user.clicksOn(mainPage.themeMenu.saveThemeButton);
        user.refreshPage();
        userSkins.opensThemeMenu();
        user.shouldSeeElement(mainPage.themeMenu.resetThemeLink);
        user.clicksOn(mainPage.themeMenu.resetThemeLink);
        userSkins.shouldSeeDefaultMordaDesign();
        user.refreshPage();
        user.shouldNotSeeElement(mainPage.themeMenu);
        userSkins.shouldSeeDefaultMordaDesign();
    }
}