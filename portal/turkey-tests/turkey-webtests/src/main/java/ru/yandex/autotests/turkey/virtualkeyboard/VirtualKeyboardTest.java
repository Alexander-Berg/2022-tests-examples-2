package ru.yandex.autotests.turkey.virtualkeyboard;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.data.VirtualKeyboardData;
import ru.yandex.autotests.turkey.pages.SerpComTrPage;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.VirtualKeyboardSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.turkey.data.VirtualKeyboardData.LANGUAGES;

/**
 * User: eoff
 * Date: 22.01.13
 */
@Aqua.Test(title = "Виртуальная клавиатура")
@Features("Virtual Keyboard")
@Stories("View")
public class VirtualKeyboardTest {
    private static final Properties CONFIG = new Properties();
    private static final Matcher<String> SERP_URL =
            matches(String.format("https?://www\\.yandex\\%s/search/\\?.*", CONFIG.getBaseDomain()));

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private VirtualKeyboardSteps userKeyboard = new VirtualKeyboardSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);
    private SerpComTrPage serpPage = new SerpComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.shouldSeeElement(yandexComTrPage.search);
    }

    @Test
    public void keyboardAppears() {
        user.shouldSeeElement(yandexComTrPage.search.keyboard);
        user.clicksOn(yandexComTrPage.search.keyboard);
        user.shouldSeeElement(yandexComTrPage.keyboard);
        user.shouldSeeElementWithText(yandexComTrPage.keyboard.switcher,
                VirtualKeyboardData.getLanguageMatcher(CONFIG.getLang()));
        user.shouldSeeElement(yandexComTrPage.keyboard.close);
        user.clicksOn(yandexComTrPage.keyboard.close);
        user.shouldNotSeeElement(yandexComTrPage.keyboard);
    }

    @Test
    public void defaultLanguage() {
        user.shouldSeeElement(yandexComTrPage.search.keyboard);
        user.clicksOn(yandexComTrPage.search.keyboard);
        user.shouldSeeElement(yandexComTrPage.keyboard);
        userKeyboard.shouldSeeKeyboardLanguage(LANGUAGES.get(CONFIG.getLang()));
    }

    @Test
    public void textAppearsInInput() {
        user.shouldSeeElement(yandexComTrPage.search.keyboard);
        user.clicksOn(yandexComTrPage.search.keyboard);
        user.shouldSeeElement(yandexComTrPage.keyboard);
        String text = userKeyboard.writeRandomText();
        user.shouldSeeInputWithText(yandexComTrPage.search.input, equalTo(text));
    }

    @Test
    public void requestThrownWhenEnterPressed() {
        user.shouldSeeElement(yandexComTrPage.search.keyboard);
        user.clicksOn(yandexComTrPage.search.keyboard);
        user.shouldSeeElement(yandexComTrPage.keyboard);
        String text = userKeyboard.writeRandomText();
        user.shouldSeeInputWithText(yandexComTrPage.search.input, equalTo(text));//для придания стабильности
        //работы тесту.
        user.shouldSeeElement(yandexComTrPage.keyboard.enter);
        user.clicksOn(yandexComTrPage.keyboard.enter);
        user.shouldSeePage(SERP_URL);
        user.shouldSeeElement(serpPage.arrow.input);
        user.shouldSeeInputWithText(serpPage.arrow.input, text);
    }
}
