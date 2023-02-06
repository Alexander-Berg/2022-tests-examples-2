package ru.yandex.autotests.morda.pages.touch.embedsearch.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.common.blocks.Suggest;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.touch.embedsearch.htmlelement.SearchForm;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: asamar
 * Date: 29.11.16
 */
@Name("Поисковый блок")
@FindBy(xpath = "//div[contains(concat(' ', @class, ' '), ' search ')]")
public class SearchBlock extends HtmlElement implements BlockWithSearchForm, BlockWithSuggest {

    private SearchForm searchForm;
    private Suggest suggest;

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

    @Override
    public HtmlElement getSuggest() {
        return suggest;
    }

    @Override
    public List<HtmlElement> getSuggestItems() {
        return suggest.items;
    }


}
