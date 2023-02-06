package ru.yandex.autotests.morda.pages.desktop.com404.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.common.blocks.VirtualKeyboardBlock;
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.desktop.com404.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithVirtualKeyboard;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;

/**
 * User: asamar
 * Date: 06.10.2015.
 */
@Name("Поисковый блок")
@FindBy(xpath = "//div[contains(@class,'layout__line_top')]")
public class SearchBlock extends HtmlElement implements BlockWithSearchForm,
        BlockWithVirtualKeyboard<VirtualKeyboardBlock>, Validateable<Com404Morda> {

    private SearchForm searchForm;
    private VirtualKeyboardBlock virtualKeyboardBlock;

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
    public HierarchicalErrorCollector validate(Validator<? extends Com404Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        searchForm.validate(validator));
    }


    @Override
    public HtmlElement getVirtualKeyboardButton() {
        return searchForm.getVirtualKeyboardButton();
    }

    @Override
    public VirtualKeyboardBlock getVirtualKeyboardBlock() {
        return virtualKeyboardBlock;
    }
}
