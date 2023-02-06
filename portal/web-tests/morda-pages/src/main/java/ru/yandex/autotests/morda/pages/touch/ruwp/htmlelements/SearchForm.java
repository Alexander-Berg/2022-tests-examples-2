package ru.yandex.autotests.morda.pages.touch.ruwp.htmlelements;

import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ruwp.TouchRuWpMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldNotSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[contains(@class, 'head-search')]")
public class SearchForm extends HtmlElement implements Validateable<TouchRuWpMorda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//button[contains(@class, 'form-button')]")
    private HtmlElement searchButton;

    @Override
    @Step("Check search form")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuWpMorda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector().check(shouldSeeElementMatchingTo(this,
                hasAttribute(HtmlAttribute.ACTION, equalTo("http://www.yandex.com.tr/touchsearch"))));
        return collector()
                .check(
                        searchFormCollector,
                        validateSearchInput(validator),
                        validateSearchButton(validator)
                );
    }

    @Step("Check search input")
    public HierarchicalErrorCollector validateSearchInput(Validator<? extends TouchRuWpMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("Check search button")
    public HierarchicalErrorCollector validateSearchButton(Validator<? extends TouchRuWpMorda> validator) {
        return collector()
                .check(shouldNotSeeElement(searchButton));
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
