package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;


/**
 * User: eoff
 * Date: 14.12.12
 */
public class SettingsButton extends HtmlElement {
    @Name("Кнопка")
    @FindBy(xpath = ".//input")
    public HtmlElement input;

    @Name("Кнопка")
    @FindBy(xpath = ".")
    public HtmlElement curr;

    @Override
    public void click() {
        if (exists().matches(input)) {
            input.click();
        } else {
            curr.click();
        }
    }
}
