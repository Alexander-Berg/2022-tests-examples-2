package ru.yandex.autotests.mordacom.steps;

import org.hamcrest.MatcherAssert;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import ru.yandex.autotests.mordacom.data.VirtualKeyboardData;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
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

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private HomePage homePage;

    public VirtualKeyboardSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.homePage = new HomePage(driver);
    }

    @Step
    public String writeRandomText() {
        String result = "";
        Random rand = new Random();
        homePage.search.input.click();
        for (int i = 0; i != VirtualKeyboardData.TEXT_LENGTH; i++) {
            int pos = rand.nextInt(VirtualKeyboardData.TOTAL_BUTTONS);
            assertThat("У списка неверный размер",
                    homePage.keyboard.buttons, hasSize(greaterThan(pos)));
            WebElement element = homePage.keyboard.buttons.get(pos);
            assertThat("Кнопка не найдена на клавиатуре", element, isDisplayed());
            element.click();
            result += element.getText();
            assertThat(homePage.search.input,
                    withWaitFor(hasText(result))
            );
        }
        return result;
    }

    @Step
    public void keyboardLanguage(Language language) {
        MatcherAssert.assertThat(homePage.keyboard.buttons,
                everyItem(hasText(inLanguage(language))));
    }

    @Step
    public void shouldSeeKeyboardLanguage(String language) {
        for (HtmlElement button : homePage.keyboard.allButtons) {
            assertThat(button, hasText(VirtualKeyboardData.LANGUAGE_SWITCHER.get(language)));
        }
    }

    @Step
    public void setKeyboardLanguage(String language) {
        for (HtmlElement lang : homePage.keyboard.allLanguages) {
            if (hasText(language).matches(lang)) {
                lang.click();
                return;
            }
        }
        fail("Язык " + language + " не найден");
    }
}