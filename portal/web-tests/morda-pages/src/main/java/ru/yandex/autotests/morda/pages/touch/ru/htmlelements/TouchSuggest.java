package ru.yandex.autotests.morda.pages.touch.ru.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: asamar
 * Date: 30.01.17
 */
@Name("Саджест")
@FindBy(xpath = "//div[@class = 'mini-suggest__popup-content']")
public class TouchSuggest extends HtmlElement {

    @Name("Элементы саджеста")
    @FindBy(xpath = ".//div")
    public List<HtmlElement> items;
}
