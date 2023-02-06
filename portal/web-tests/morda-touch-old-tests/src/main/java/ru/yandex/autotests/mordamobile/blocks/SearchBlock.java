package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок поиска")
@FindBy(xpath = "//div[contains(@class, 'b-head-search__bottom')]")
public class SearchBlock extends HtmlElement {
    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@type='search']")
    public TextInput input;

    @Name("Кнопка 'Найти'")
    @FindBy(xpath = ".//button")
    public HtmlElement searchButton;

    @Name("Саджест")
    @FindBy(xpath = "//div[contains(@class, 'b-form-input__popup')]")
    public HtmlElement suggest;

    @Name("Список табов")
    @FindBy(xpath = "//div[contains(@class, 'b-tabs-simple')]//a")
    public List<HtmlElement> allTabs;
}
