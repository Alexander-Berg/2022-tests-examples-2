package ru.yandex.autotests.morda.pages.desktop.firefox.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.language.Dictionary;
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
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 26.08.2015.
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[contains(@class, 'suggest2-form')]")
public class SearchForm extends HtmlElement implements BlockWithSearchForm, Validateable<DesktopFirefoxMorda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Параметр lr")
    @FindBy(xpath = ".//input[@name='lr']")
    private HtmlElement lr;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//button[contains(@type, 'submit')]")
    private HtmlElement searchButton;

    @Step("Check search input")
    public HierarchicalErrorCollector validateSearchInput(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("Check lr")
    public HierarchicalErrorCollector validateLr(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(
                        shouldExistElement(lr),
                        shouldSeeElementMatchingTo(lr,
                                hasAttribute(VALUE, equalTo(validator.getCleanvars().getGeoID() + "")))
                );
    }

    @Step("Check search button")
    public HierarchicalErrorCollector validateSearchButton(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(
                        shouldSeeElement(searchButton),
                        shouldSeeElementMatchingTo(searchButton,
                                hasText(getTranslation(Dictionary.Home.Main.SEARCH, validator.getMorda().getLanguage())))
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

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopFirefoxMorda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector().check(shouldSeeElementMatchingTo(this,
                hasAttribute(ACTION, equalTo(validator.getCleanvars().getSearch().getUrl()))));

        return collector()
                .check(
                        shouldSeeElement(this)
                )
                .check(
                        searchFormCollector,
                        validateSearchInput(validator),
                        validateSearchButton(validator),
                        validateLr(validator)
                );
    }
}
