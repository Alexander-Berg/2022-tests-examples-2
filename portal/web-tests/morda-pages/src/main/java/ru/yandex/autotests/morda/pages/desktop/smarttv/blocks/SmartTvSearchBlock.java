package ru.yandex.autotests.morda.pages.desktop.smarttv.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.common.blocks.Suggest;
import ru.yandex.autotests.morda.pages.desktop.smarttv.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: asamar
 * Date: 18.11.16
 */
@Name("Поисковый блок")
@FindBy(xpath = "//div[contains(@class, 'main__row_arrow')]")
public class SmartTvSearchBlock extends HtmlElement implements BlockWithSearchForm, BlockWithSuggest {

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
