package ru.yandex.autotests.morda.pages.pda.ru.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.pda.ru.PdaRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldExistElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.ACTION;

/**
 * User: asamar
 * Date: 26.08.2015.
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[@id='web']")
public class SearchForm extends HtmlElement implements BlockWithSearchForm, Validateable<PdaRuMorda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Параметр lr")
    @FindBy(xpath = ".//input[@name='lr']")
    private HtmlElement lr;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//input[contains(@type, 'submit')]")
    private HtmlElement searchButton;

    @Override
    @Step("Check search form")
    public HierarchicalErrorCollector validate(Validator<? extends PdaRuMorda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector().check(shouldSeeElementMatchingTo(this,
                hasAttribute(ACTION, equalTo("https://www.yandex.com/yandsearch"))));

        return collector()
                .check(
                        searchFormCollector,
                        validateSearchInput(validator),
                        validateSearchButton(validator),
                        validateLr(validator)
                );
    }

    @Step("Check search input")
    public HierarchicalErrorCollector validateSearchInput(Validator<? extends PdaRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("Check lr")
    public HierarchicalErrorCollector validateLr(Validator<? extends PdaRuMorda> validator) {
        return collector()
                .check(
                        shouldExistElement(lr)
                );
    }

    @Step("Check search button")
    public HierarchicalErrorCollector validateSearchButton(Validator<? extends PdaRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchButton));
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
