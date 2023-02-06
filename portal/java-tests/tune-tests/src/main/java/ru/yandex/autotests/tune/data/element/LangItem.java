package ru.yandex.autotests.tune.data.element;

import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.ExtendedWebElement;
import io.qameta.htmlelements.element.HtmlElement;

/**
 * User: asamar
 * Date: 24.11.16
 */
public interface LangItem extends ExtendedWebElement<LangItem> {

    @FindBy(".//input")
    HtmlElement input();

    default boolean isSelected() {
//        return "true".equals(input().getAttribute("checked"));
        return input().getAttribute("checked") != null;
    }

    default String getValue() {
        return input().getAttribute("value");
    }
}
