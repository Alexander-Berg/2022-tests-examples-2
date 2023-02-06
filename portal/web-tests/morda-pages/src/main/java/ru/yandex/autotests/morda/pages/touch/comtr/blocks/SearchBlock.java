package ru.yandex.autotests.morda.pages.touch.comtr.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithTabs;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.SearchTab;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.SearchTabs;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.Suggest;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
@Name("Поисковый блок")
@FindBy(xpath = "//div[contains(@class, 'content__body')]")
public class SearchBlock extends HtmlElement implements BlockWithSearchForm, BlockWithSuggest,
        BlockWithTabs<SearchTab>, Validateable<TouchComTrMorda>
{

    private SearchForm searchForm;
    private Suggest suggest;
    private SearchTabs searchTabs;

    @Override
    public HtmlElement getSuggest() {
        return suggest;
    }

    @Override
    public List<HtmlElement> getSuggestItems() {
        return suggest.getSuggestItems();
    }

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
    public List<? extends SearchTab> getSearchTabs() {
        return searchTabs.getSearchTabs();
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(
                        searchForm.validate(validator),
                        searchTabs.validate(validator)
                );
    }

}
