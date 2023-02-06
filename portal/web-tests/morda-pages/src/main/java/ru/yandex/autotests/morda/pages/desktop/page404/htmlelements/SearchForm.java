package ru.yandex.autotests.morda.pages.desktop.page404.htmlelements;

import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.ACTION;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[contains(@class, 'morda-search-form')]")
public class SearchForm extends HtmlElement implements BlockWithSearchForm, Validateable<Desktop404Morda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//input[contains(@type, 'submit')]")
    private HtmlElement searchButton;

    @Override
    @Step("Check search form")
    public HierarchicalErrorCollector validate(Validator<? extends Desktop404Morda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector()
                .check(shouldSeeElementMatchingTo(this,
                        hasAttribute(ACTION, equalTo("https://www.yandex.com.tr/yandsearch")))
                );

        return collector()
                .check(
                        searchFormCollector,
                        validateSearchInput(validator),
                        validateSearchButton(validator)
                );
    }

    @Step("Check search input")
    public HierarchicalErrorCollector validateSearchInput(Validator<? extends Desktop404Morda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("Check search button")
    public HierarchicalErrorCollector validateSearchButton(Validator<? extends Desktop404Morda> validator) {
        return collector()
                .check(shouldSeeElement(searchButton));
    }

    public TextInput getSearchInput() {
        return searchInput;
    }

    public HtmlElement getLr() {
        throw new NoSuchElementException("lr is not present on this page");
    }

    public HtmlElement getSearchButton() {
        return searchButton;
    }
}
