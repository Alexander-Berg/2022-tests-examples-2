package ru.yandex.autotests.hwmorda.data;

import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 13.09.12
 */
public class RubricButton extends HtmlElement {
    @Override
    public boolean isSelected() {
        return getWrappedElement().getAttribute("class").contains("cur");
    }
}
