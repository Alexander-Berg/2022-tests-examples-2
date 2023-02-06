package ru.yandex.autotests.morda.pages.common.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: asamar
 * Date: 29.11.16
 */
@Name("Саджест")
@FindBy(xpath = "//div[contains(@class, 'mini-suggest__popup-content')]|//ul[contains(@class, 'suggest2__content')]")
public class Suggest extends HtmlElement {
    @Name("Элементы саджеста")
    @FindBy(xpath = ".//div[contains(@class, 'suggest__item')]|//li[contains(@class, 'suggest2-item')]")
    public List<HtmlElement> items;

}
