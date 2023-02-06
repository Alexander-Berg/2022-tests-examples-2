package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.common.blocks.Suggest;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.pages.touch.ru.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.touch.ru.htmlelements.SearchTabs;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
@Name("Поисковый блок")
//@FindBy(xpath = "//div[contains(concat(' ', @class, ' '), ' search ')]")
@FindBy(xpath = "//div[@class = 'content__bg']")
public class SearchBlock extends HtmlElement implements BlockWithSearchForm, BlockWithSuggest, Validateable<TouchRuMorda> {

    private SearchForm searchForm;
    private SearchTabs searchTabs;
    private Suggest suggest;

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        searchForm.validate(validator),
                        searchTabs.validate(validator)
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
        return suggest.items;
    }
}
