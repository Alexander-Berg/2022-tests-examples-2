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

import static ru.yandex.autotests.mainmorda.data.SkinsData.RANDOM_SKIN;
import static ru.yandex.autotests.mainmorda.data.SkinsData.RANDOM_SKIN_2;
import static ru.yandex.autotests.mainmorda.data.SkinsData.SHARE_TITLE_MATCHER;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;

/**
 * User: alex89
 * Date: 01.08.12
 */
@Aqua.Test(title = "Проверка блока 'Поделиться темой' в примерочной скинов")
@Features({"Main", "Common", "Skins"})
@Stories("Share")
public class ShareSkinTest {
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
    public void noShareBlockWithDefaultDesign() {
        userSkins.opensThemeMenu();
        user.shouldNotSeeElement(mainPage.themeMenu.shareBlock);
    }

    @Test
    public void shareBlockWithSelectedSkin() {
        userSkins.opensThemeMenu();
        userSkins.setSkinWithUrl(RANDOM_SKIN);
        user.shouldSeeElement(mainPage.themeMenu.shareBlock);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.shareBlock,
                hasAttribute(TITLE, SHARE_TITLE_MATCHER));
        userSkins.shouldSeeSocialIcons(RANDOM_SKIN);
    }

    @Test
    public void shareBlockWithSavedSkin() {
        userSkins.savesSkinWithUrl(RANDOM_SKIN);
        userSkins.opensThemeMenu();

        user.shouldSeeElement(mainPage.themeMenu.shareBlock);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.shareBlock,
                hasAttribute(TITLE, SHARE_TITLE_MATCHER));
        userSkins.shouldSeeSocialIcons(RANDOM_SKIN);
    }

    @Test
    public void shareBlockWithSelectedSkinWhileSelectingAnotherSkin() {
        userSkins.savesSkinWithUrl(RANDOM_SKIN);
        userSkins.opensThemeMenu();
        userSkins.setSkinWithUrl(RANDOM_SKIN_2);
        user.shouldSeeElement(mainPage.themeMenu.shareBlock);
        user.shouldSeeElementMatchingTo(mainPage.themeMenu.shareBlock,
                hasAttribute(TITLE, SHARE_TITLE_MATCHER));
        userSkins.shouldSeeSocialIcons(RANDOM_SKIN_2);
    }
}