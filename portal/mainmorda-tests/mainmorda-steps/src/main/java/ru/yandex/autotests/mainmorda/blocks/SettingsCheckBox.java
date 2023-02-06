package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;

/**
 * User: eoff
 * Date: 17.12.12
 */
public class SettingsCheckBox extends CheckBox {

    @Name("Чекбокс")
    @FindBy(xpath = ".//input")
    public CheckBox input;

    @Override
    public void select() {
        input.select();
    }

    @Override
    public void deselect() {
        input.deselect();
    }

    @Override
    public boolean isSelected() {
        return input.isSelected();
    }
}
