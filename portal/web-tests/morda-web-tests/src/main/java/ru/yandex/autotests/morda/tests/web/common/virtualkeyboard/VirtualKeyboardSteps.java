package ru.yandex.autotests.morda.tests.web.common.virtualkeyboard;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import ru.yandex.autotests.morda.pages.common.blocks.VirtualKeyboardBlock;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.Random;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.isDisplayed;

/**
 * User: eoff
 * Date: 22.01.13
 */
public class VirtualKeyboardSteps {

    private WebDriver driver;
    private CommonMordaSteps userSteps;

    public VirtualKeyboardSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step
    public String writeRandomText(TextInput searchInput, VirtualKeyboardBlock keyboard) {
        String result = "";
        Random rand = new Random();
        searchInput.click();
        for (int i = 0; i != VirtualKeyboardData.TEXT_LENGTH; i++) {
            int pos = rand.nextInt(VirtualKeyboardData.TOTAL_BUTTONS);
            assertThat("У списка неверный размер",
                    keyboard.buttons, hasSize(greaterThan(pos)));
            WebElement element = keyboard.buttons.get(pos);
            assertThat("Кнопка не найдена на клавиатуре", element, isDisplayed());
            element.click();
            result += element.getText();
            assertThat(searchInput,
                    withWaitFor(hasText(result))
            );
        }
        return result;
    }

    @Step
    public void shouldSeeKeyboardLanguage(VirtualKeyboardBlock keyboard, String language) {
        for (HtmlElement button : keyboard.allButtons) {
            assertThat(button, hasText(VirtualKeyboardData.LANGUAGE_SWITCHER.get(language)));
        }
    }

    @Step
    public void setKeyboardLanguage(VirtualKeyboardBlock keyboard, String language) {
        for (HtmlElement lang : keyboard.allLanguages) {
            if (hasText(language).matches(lang)) {
                lang.click();
                return;
            }
        }
        fail("Язык " + language + " не найден");
    }
}