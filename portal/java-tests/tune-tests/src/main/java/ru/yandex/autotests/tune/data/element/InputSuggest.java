package ru.yandex.autotests.tune.data.element;

import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.ExtendedList;
import io.qameta.htmlelements.element.ExtendedWebElement;
import io.qameta.htmlelements.element.HtmlElement;

/**
 * User: asamar
 * Date: 27.12.16
 */
public interface InputSuggest extends ExtendedWebElement<InputSuggest> {

    @FindBy(".//li[contains(@class, 'b-autocomplete-item_type_geo')]")
    ExtendedList<Item> items();

    interface Item extends ExtendedWebElement<Item> {

        @FindBy(".//div[@class = 'b-autocomplete-item__reg']")
        HtmlElement city();


        @FindBy(".//div[@class = 'b-autocomplete-item__details']")
        HtmlElement region();
    }
}
