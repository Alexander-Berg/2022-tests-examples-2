package ru.yandex.autotests.tune.data.element;

import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.ExtendedWebElement;
import io.qameta.htmlelements.element.HtmlElement;

import static io.qameta.htmlelements.matcher.DisplayedMatcher.displayed;

/**
 * User: asamar
 * Date: 14.12.16
 */
public interface CheckBox extends ExtendedWebElement<CheckBox> {

    @FindBy(".//label")
    HtmlElement label();

    @FindBy(".//span")
    HtmlElement span();

    @FindBy(".//input")
    HtmlElement input();


    default boolean isChecked(){
        return this.getAttribute("class").contains("checkbox_checked_yes");
    }

    default void check() {
        if (!isChecked()) {
            label().should(displayed()).click();
        }
    }

    default void unCheck() {
        if (isChecked()) {
            label().should(displayed()).click();
        }
    }

}
