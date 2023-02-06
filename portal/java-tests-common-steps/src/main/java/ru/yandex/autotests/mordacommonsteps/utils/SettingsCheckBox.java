package ru.yandex.autotests.mordacommonsteps.utils;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.CheckBox;

/**
 * User: asamar
 * Date: 26.08.16
 */

public class SettingsCheckBox extends HtmlElement implements Selectable {

    @FindBy(xpath = "./input")
    public CheckBox input;

    @Override
    public void select() {
        if (!isSelected()) {
            input.select();
        }
    }

    @Override
    public void deselect() {
        if (isSelected()) {
            input.deselect();
        }
    }

    @Override
    public boolean isSelected(){
        return input.getWrappedElement().isSelected();
    }
}
