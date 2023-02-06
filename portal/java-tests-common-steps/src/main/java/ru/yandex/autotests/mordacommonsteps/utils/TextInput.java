package ru.yandex.autotests.mordacommonsteps.utils;

import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 12.03.13
 */
public class TextInput extends HtmlElement {

    @Override
    public String getText() {
        String enteredText = getAttribute("value");
        if (enteredText == null) {
            return "";
        }
        return enteredText;
    }
}
