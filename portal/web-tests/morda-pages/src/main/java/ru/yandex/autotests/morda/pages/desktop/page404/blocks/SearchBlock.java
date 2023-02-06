package ru.yandex.autotests.morda.pages.desktop.page404.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.page404.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
@Name("Поисковый блок")
@FindBy(xpath = "//div[contains(@class, 'search-decor')]")
public class SearchBlock extends HtmlElement implements BlockWithSearchForm {

    private SearchForm searchForm;

    @Override
    public TextInput getSearchInput() {
        return searchForm.getSearchInput();
    }

    @Override
    public HtmlElement getSearchButton() {
        return searchForm.getSearchButton();
    }

    @Override
    public HtmlElement getLr() {
        return searchForm.getLr();
    }

}
