package ru.yandex.autotests.turkey.virtualkeyboard;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.data.VirtualKeyboardData;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.VirtualKeyboardSteps;
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
@Features("Virtual Keyboard")
@Stories("Languages")
public class VirtualKeyboardLanguagesTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private VirtualKeyboardSteps userKeyboard = new VirtualKeyboardSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

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
        user.opensPage(CONFIG.getBaseURL());
        user.shouldSeeElement(yandexComTrPage.search);
        user.shouldSeeElement(yandexComTrPage.search.keyboard);
        user.clicksOn(yandexComTrPage.search.keyboard);
        user.shouldSeeElement(yandexComTrPage.keyboard);
    }

    @Test
    public void allLanguages() {
        user.shouldSeeElement(yandexComTrPage.keyboard.switcher);
        user.clicksOn(yandexComTrPage.keyboard.switcher);
        user.shouldSeeElement(yandexComTrPage.keyboard.allLanguagesPopup);
        userKeyboard.setKeyboardLanguage(language);
        userKeyboard.shouldSeeKeyboardLanguage(language);
    }
}
