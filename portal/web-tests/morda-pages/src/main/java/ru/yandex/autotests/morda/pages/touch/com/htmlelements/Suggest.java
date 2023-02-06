package ru.yandex.autotests.morda.pages.touch.com.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Саджест")
@FindBy(xpath = "//div[contains(@class, 'suggest__popup-content')]")
public class Suggest extends HtmlElement {

    @Name("Элементы саджеста")
    @FindBy(xpath = ".//div[contains(@class, 'suggest__item')]")
    private List<HtmlElement> suggestItems;

    public List<HtmlElement> getSuggestItems() {
        return suggestItems;
    }
}
