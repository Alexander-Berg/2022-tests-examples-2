package ru.yandex.autotests.morda.pages.touch.ru.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static java.lang.String.valueOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[contains(@class, 'search3')]|//form[contains(@class, 'suggest2-form')]")
public class SearchForm extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Параметр lr")
    @FindBy(xpath = ".//input[@name='lr']")
    private HtmlElement lr;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//button[@type='submit']")
    private HtmlElement searchButton;

    @Override
    @Step("Check search form")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector().check(shouldSeeElementMatchingTo(this,
                hasAttribute(HtmlAttribute.ACTION, equalTo(validator.getCleanvars().getSearchUrl()))));
        return collector()
                .check(
                        searchFormCollector,
                        validateSearchInput(validator),
                        validateSearchButton(validator),
                        validateLr(validator)
                );
    }

    @Step("Check search input")
    public HierarchicalErrorCollector validateSearchInput(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("Check lr")
    public HierarchicalErrorCollector validateLr(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        shouldSeeElementMatchingTo(lr,
                                hasAttribute(VALUE, equalTo(valueOf(validator.getCleanvars().getGeoID()))))
                );
    }

    @Step("Check search button")
    public HierarchicalErrorCollector validateSearchButton(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        shouldSeeElement(searchButton),
                        shouldSeeElementMatchingTo(searchButton,
                                hasText(getTranslation("home", "main", "search", validator.getMorda().getLanguage()).toUpperCase()))
                );
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
