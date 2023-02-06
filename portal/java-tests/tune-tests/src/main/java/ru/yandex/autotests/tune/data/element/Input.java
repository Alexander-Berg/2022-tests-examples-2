package ru.yandex.autotests.tune.data.element;

import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.ExtendedWebElement;
import io.qameta.htmlelements.element.HtmlElement;
import org.hamcrest.text.IsEmptyString;
import ru.yandex.autotests.morda.matchers.HtmlAttributeMatcher;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.CoreMatchers.not;
import static ru.yandex.autotests.morda.matchers.HtmlAttributeMatcher.HtmlAttribute.VALUE;

/**
 * User: asamar
 * Date: 14.12.16
 */
public interface Input extends ExtendedWebElement<Input>{

    @FindBy(".//label[@class = 'input__filled-hint']")
    HtmlElement label();

    @FindBy(".//span[@class = 'input__box']")
    HtmlElement inputBox();

    @FindBy(".//span[@class = 'input__geo']")
    HtmlElement inputGeo();

    @FindBy(".//input")
    HtmlElement input();

    @Step("Write text \"{0}\"")
    default void entersTextInInput(String text) {
        input().clear();
        input().waitUntil("Не дождались отчистки поля ввода", HtmlAttributeMatcher.hasAttribute(VALUE, IsEmptyString.isEmptyOrNullString()));
        input().sendKeys(text);
        input().waitUntil("Не дождались текста " + text + " в поле ввода", HtmlAttributeMatcher.hasAttribute(VALUE, not(IsEmptyString.isEmptyOrNullString())));
    }

}
