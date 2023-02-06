package ru.yandex.autotests.mordacommonsteps.utils;

import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 04.03.13
 */
public class CheckBox extends HtmlElement implements Selectable {
    @Override
    public void select() {
        if (!isSelected()) {
            getWrappedElement().click();
        }
    }

    @Override
    public void deselect() {
        if (isSelected()) {
            getWrappedElement().click();
        }
    }

    @Override
    public boolean isSelected() {
        return getWrappedElement().isSelected();
    }
}
