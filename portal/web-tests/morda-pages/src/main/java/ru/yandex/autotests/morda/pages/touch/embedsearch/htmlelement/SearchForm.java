package ru.yandex.autotests.morda.pages.touch.embedsearch.htmlelement;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: asamar
 * Date: 29.11.16
 */
@Name("Поисковая форма")
@FindBy(xpath = ".//form[contains(@class, 'search-arrow')]")
public class SearchForm extends HtmlElement {
    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Параметр lr")
    @FindBy(xpath = ".//input[@name='lr']")
    private HtmlElement lr;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//button[@type='submit']")
    private HtmlElement searchButton;

    public TextInput getSearchInput() {
        return searchInput;
    }

    public HtmlElement getLr() {
        return lr;
    }

    public HtmlElement getSearchButton() {
        return searchButton;
    }
}
