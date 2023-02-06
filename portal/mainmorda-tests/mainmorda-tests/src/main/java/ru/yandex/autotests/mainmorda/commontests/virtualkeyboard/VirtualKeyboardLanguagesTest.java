package ru.yandex.autotests.mainmorda.commontests.virtualkeyboard;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.VirtualKeyboardData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.VirtualKeyboardSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

/**
 * User: eoff
 * Date: 11.03.13
 */
@Aqua.Test(title = "Переключение языков в виртуальной клавиатуре")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Virtual Keyboard"})
@Stories("Languages")
public class VirtualKeyboardLanguagesTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private VirtualKeyboardSteps userKeyboard = new VirtualKeyboardSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(VirtualKeyboardData.LANGUAGE_SWITCHER.keySet());
    }

    private String language;

    public VirtualKeyboardLanguagesTest(String language) {
        this.language = language;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.search);
        user.shouldSeeElement(mainPage.search.keyboard);
        user.clicksOn(mainPage.search.keyboard);
        user.shouldSeeElement(mainPage.keyboard);
    }

    @Test
    public void allLanguages() {
        user.shouldSeeElement(mainPage.keyboard.switcher);
        user.clicksOn(mainPage.keyboard.switcher);
        user.shouldSeeElement(mainPage.keyboard.allLanguagesPopup);
        userKeyboard.setKeyboardLanguage(language);
        userKeyboard.shouldSeeKeyboardLanguage(language);
    }
}
