package ru.yandex.autotests.morda.pages.touch.com.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.com.TouchComMorda;
import ru.yandex.autotests.morda.pages.touch.com.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.touch.com.htmlelements.Suggest;
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
public class SearchBlock extends HtmlElement implements BlockWithSearchForm, BlockWithSuggest, Validateable<TouchComMorda> {

    private SearchForm searchForm;
    private Suggest suggest;

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchComMorda> validator) {
        return collector()
                .check(
                        searchForm.validate(validator)
                );
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
    public HtmlElement getSuggest() {
        return suggest;
    }

    @Override
    public List<HtmlElement> getSuggestItems() {
        return suggest.getSuggestItems();
    }
}
