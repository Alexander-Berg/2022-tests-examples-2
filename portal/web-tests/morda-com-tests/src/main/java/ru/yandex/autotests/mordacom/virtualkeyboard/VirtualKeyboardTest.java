package ru.yandex.autotests.mordacom.virtualkeyboard;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.data.VirtualKeyboardData;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacom.pages.SerpComPage;
import ru.yandex.autotests.mordacom.steps.VirtualKeyboardSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacom.data.VirtualKeyboardData.LANGUAGES;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * User: eoff
 * Date: 22.01.13
 */
@Aqua.Test(title = "Виртуальная клавиатура")
@Features("Virtual Keyboard")
@Stories("View")
@RunWith(Parameterized.class)
public class VirtualKeyboardTest {
    private static final Properties CONFIG = new Properties();
    private static final Matcher<String> SERP_URL =
            matches(String.format("https?://www\\.yandex\\%s/search/\\?.*", CONFIG.getBaseDomain()));

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private VirtualKeyboardSteps userKeyboard = new VirtualKeyboardSteps(driver);
    private HomePage mainPage = new HomePage(driver);
    private SerpComPage serpPage = new SerpComPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CONFIG.getMordaComLangs());
    }

    private final Language language;

    public VirtualKeyboardTest(Language language) {
        this.language = language;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(mainPage.search);
    }

    @Test
    public void keyboardAppears() {
        user.shouldSeeElement(mainPage.search.keyboard);
        user.clicksOn(mainPage.search.keyboard);
        user.shouldSeeElement(mainPage.keyboard);
        user.shouldSeeElementWithText(mainPage.keyboard.switcher,
                VirtualKeyboardData.getLanguageMatcher(language));
        user.shouldSeeElement(mainPage.keyboard.close);
        user.clicksOn(mainPage.keyboard.close);
        user.shouldNotSeeElement(mainPage.keyboard);
    }

    @Test
    public void defaultLanguage() {
        user.shouldSeeElement(mainPage.search.keyboard);
        user.clicksOn(mainPage.search.keyboard);
        user.shouldSeeElement(mainPage.keyboard);
        userKeyboard.shouldSeeKeyboardLanguage(LANGUAGES.get(language));
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
        user.shouldSeeElement(serpPage.arrow.input);
        user.shouldSeeInputWithText(serpPage.arrow.input, text);
    }
}
