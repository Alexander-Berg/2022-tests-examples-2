package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.Selectable;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/15
 */
public class SelectableTab extends HtmlElement implements Selectable {

    @FindBy(xpath = ".//a")
    private HtmlElement link;

    @Override
    public void click() {
        link.click();
    }

    @Override
    public void select() {
        if (isSelected()) {
            return;
        }
        click();
    }

    @Override
    public void deselect() {
        if (!isSelected()) {
            return;
        }
        click();
    }

    @Override
    public boolean isSelected() {
        return this.getAttribute("aria-selected").equals("true");
    }
}
