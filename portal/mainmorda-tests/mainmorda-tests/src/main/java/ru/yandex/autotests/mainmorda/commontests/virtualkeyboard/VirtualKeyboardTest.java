package ru.yandex.autotests.mainmorda.commontests.virtualkeyboard;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.VirtualKeyboardData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.pages.SerpPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.VirtualKeyboardSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * User: eoff
 * Date: 22.01.13
 */
@Aqua.Test(title = "Виртуальная клавиатура")
@Features({"Main", "Common", "Virtual Keyboard"})
@Stories("View")
public class VirtualKeyboardTest {
    private static final Properties CONFIG = new Properties();
    private static final Matcher<String> SERP_URL =
            matches(String.format("https?://yandex\\%s/search/\\?.*", CONFIG.getBaseDomain()));

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private VirtualKeyboardSteps userKeyboard = new VirtualKeyboardSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private SerpPage serpPage = new SerpPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.search);
    }

    @Test
    public void keyboardAppears() {
        user.shouldSeeElement(mainPage.search.keyboard);
        user.clicksOn(mainPage.search.keyboard);
        user.shouldSeeElement(mainPage.keyboard);
        user.shouldSeeElementWithText(mainPage.keyboard.switcher,
                VirtualKeyboardData.LANGUAGE);
        user.shouldSeeElement(mainPage.keyboard.close);
        user.clicksOn(mainPage.keyboard.close);
        user.shouldNotSeeElement(mainPage.keyboard);
    }

    @Test
    public void defaultLanguage() {
        user.shouldSeeElement(mainPage.search.keyboard);
        user.clicksOn(mainPage.search.keyboard);
        user.shouldSeeElement(mainPage.keyboard);
        userKeyboard.keyboardLanguage();
    }

    @Test
    public void noKeyboardIconInEditMode() {
        userMode.setEditMode();
        user.shouldNotSeeElement(mainPage.search.keyboard);
    }

    @Test
    public void textAppearsInInput() {
        user.shouldSeeElement(mainPage.search.keyboard);
        user.clicksOn(mainPage.search.keyboard);
        user.shouldSeeElement(mainPage.keyboard);
        String text = userKeyboard.writeRandomText();
        user.shouldSeeInputWithText(mainPage.search.input, equalTo(text));
    }

    @Test
    public void requestThrownWhenEnterPressed() {
        user.shouldSeeElement(mainPage.search.keyboard);
        user.clicksOn(mainPage.search.keyboard);
        user.shouldSeeElement(mainPage.keyboard);
        String text = userKeyboard.writeRandomText();
        user.shouldSeeInputWithText(mainPage.search.input, equalTo(text));//для придания стабильности
        //работы тесту.
        user.shouldSeeElement(mainPage.keyboard.enter);
        user.clicksOn(mainPage.keyboard.enter);
        user.shouldSeePage(SERP_URL);
        user.shouldSeeElement(serpPage.search.input);
        user.shouldSeeInputWithText(serpPage.search.input, text);
    }
}
