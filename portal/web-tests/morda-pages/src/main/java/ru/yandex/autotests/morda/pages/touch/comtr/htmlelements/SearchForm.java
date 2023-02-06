package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static java.lang.String.valueOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldExistElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldNotSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;

/**
 * User: asamar
 * Date: 26.08.2015.
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[@role='search']")
public class SearchForm extends HtmlElement implements Validateable<TouchComTrMorda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Параметр lr")
    @FindBy(xpath = ".//input[@name='lr']")
    private HtmlElement lr;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//button[contains(@type, 'submit')]")
    private HtmlElement searchButton;

    @Override
    @Step("Check search form")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector().check(shouldSeeElementMatchingTo(this,
                hasAttribute(HtmlAttribute.ACTION, equalTo(validator.getMorda().getSerpUrl().toString()))));

        return collector()
                .check(
                        searchFormCollector,
                        validateSearchInput(validator),
                        validateSearchButton(validator),
                        validateLr(validator)
                );
    }

    @Step("Check search input")
    public HierarchicalErrorCollector validateSearchInput(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("Check lr")
    public HierarchicalErrorCollector validateLr(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldExistElement(lr))
                .check(
                        shouldSeeElementMatchingTo(lr,
                                hasAttribute(VALUE, equalTo(valueOf(validator.getMorda().getRegion().getRegionId()))))
                );
    }

    @Step("Check search button")
    public HierarchicalErrorCollector validateSearchButton(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldNotSeeElement(searchButton));
    }

    public TextInput getSearchInput() {
        return searchInput;
    }

    public HtmlElement getLr() {
        return lr;
    }

    public HtmlElement getSearchButton() {
        return searchButton;
    }

}
