package ru.yandex.autotests.morda.pages.desktop.firefox.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.common.blocks.Suggest;
import ru.yandex.autotests.morda.pages.common.blocks.VirtualKeyboardBlock;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.desktop.firefox.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.desktop.firefox.htmlelements.SearchTabs;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithVirtualKeyboard;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
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

@FindBy(xpath = "//table[contains(@class,'main-table')]")
public class SearchBlock extends HtmlElement implements BlockWithSuggest, BlockWithVirtualKeyboard<VirtualKeyboardBlock>,
        Validateable<DesktopFirefoxMorda> {

    private SearchForm searchForm;
    private Suggest suggest;
    private SearchTabs searchTabs;

    private VirtualKeyboardBlock virtualKeyboardBlock;

    @Name("иконка клавиатуры")
    @FindBy(xpath = ".//div[contains(@class,' keyboard-loader')]/i")
    public HtmlElement virtualKeyboardButton;

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
    public HtmlElement getVirtualKeyboardButton() {
        return virtualKeyboardButton;
    }

    @Override
    public VirtualKeyboardBlock getVirtualKeyboardBlock() {
        return virtualKeyboardBlock;
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(
                        searchForm.validate(validator),
                        searchTabs.validate(validator)
                );
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
