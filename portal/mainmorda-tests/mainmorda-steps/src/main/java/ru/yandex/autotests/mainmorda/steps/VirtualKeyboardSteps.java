package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.MatcherAssert;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.VirtualKeyboardData;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.Random;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.core.Every.everyItem;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.isDisplayed;

/**
 * User: eoff
 * Date: 22.01.13
 */
public class VirtualKeyboardSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;

    public VirtualKeyboardSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new MainPage(driver);
    }

    @Step
    public String writeRandomText() {
        String result = "";
        Random rand = new Random();
        basePage.search.input.click();
        for (int i = 0; i != VirtualKeyboardData.TEXT_LENGTH; i++) {
            int pos = rand.nextInt(VirtualKeyboardData.TOTAL_BUTTONS);
            assertThat("У списка неверный размер",
                    basePage.keyboard.buttons, hasSize(greaterThan(pos)));
            WebElement element = basePage.keyboard.buttons.get(pos);
            assertThat("Кнопка не найдена на клавиатуре", element, isDisplayed());
            element.click();
            result += element.getText();
            assertThat(basePage.search.input,
                    withWaitFor(hasText(result))
            );
        }
        return result;
    }

    @Step
    public void keyboardLanguage() {
        MatcherAssert.assertThat(basePage.keyboard.buttons,
                everyItem(hasText(inLanguage(CONFIG.getLang()))));
    }

    @Step
    public void shouldSeeKeyboardLanguage(String language) {
        for (HtmlElement button : basePage.keyboard.allButtons) {
            assertThat(button, hasText(VirtualKeyboardData.LANGUAGE_SWITCHER.get(language)));
        }
    }

    @Step
    public void setKeyboardLanguage(String language) {
        for (HtmlElement lang : basePage.keyboard.allLanguages) {
            if (hasText(language).matches(lang)) {
                lang.click();
                return;
            }
        }
        fail("Язык " + language + " не найден");
    }
}