package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: ivannik
 * Date: 14.09.2014
 */
@Name("Блок табов")
@FindBy(xpath = "//div[@class='tabs']")
public class TabsBlock extends HtmlElement {

    @Name("Список табов")
    @FindBy(xpath = ".//a")
    public List<Tab> tabs;

    public static class Tab extends HtmlElement {

        @Name("Иконка svg")
        @FindBy(xpath = "./div[contains(@class, 'tabs__item__image')]")
        public HtmlElement icon;

        @Name("Подпись иконки")
        @FindBy(xpath = "./div[contains(@class, 'tabs__item__text')]")
        public HtmlElement tabText;
    }
}
