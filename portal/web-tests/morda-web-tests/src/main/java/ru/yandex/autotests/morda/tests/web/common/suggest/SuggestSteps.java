package ru.yandex.autotests.morda.tests.web.common.suggest;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 02/03/15
 */
public class SuggestSteps {
    private WebDriver driver;
    private CommonMordaSteps userSteps;

    public SuggestSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step("Write text \"{1}\" in input ")
    public void appendsTextInInputSlowly(TextInput textInput, String text) throws InterruptedException {
        for (char ch : text.toCharArray()) {
            userSteps.appendsTextInInput(textInput, String.valueOf(ch));
            Thread.sleep(50);
        }
    }
}
