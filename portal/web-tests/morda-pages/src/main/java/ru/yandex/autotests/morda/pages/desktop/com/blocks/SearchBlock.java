package ru.yandex.autotests.morda.pages.desktop.com.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.common.blocks.Suggest;
import ru.yandex.autotests.morda.pages.common.blocks.VirtualKeyboardBlock;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.com.htmlelements.SearchForm;
import ru.yandex.autotests.morda.pages.desktop.com.htmlelements.TabsForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithTabs;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithVirtualKeyboard;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
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
@FindBy(xpath = "//div[contains(@class,'b-line__center')]")
public class SearchBlock extends HtmlElement implements BlockWithSearchForm, BlockWithTabs<TabsForm.Tab>,
        BlockWithSuggest, BlockWithVirtualKeyboard<VirtualKeyboardBlock>, Validateable<DesktopComMorda> {

    private SearchForm searchForm;
    private TabsForm tabsForm;
    private Suggest suggest;
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
    public List<TabsForm.Tab> getSearchTabs() {
        return tabsForm.getTabs();
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        searchForm.validate(validator),
                        tabsForm.validate(validator));
    }


    @Override
    public HtmlElement getVirtualKeyboardButton() {
        return searchForm.getVirtualKeyboardButton();
    }

    @Override
    public VirtualKeyboardBlock getVirtualKeyboardBlock() {
        return virtualKeyboardBlock;
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
