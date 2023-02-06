package ru.yandex.autotests.morda.pages.desktop.yaru.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.ACTION;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 26.08.2015.
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[contains(@class, 'suggest2-form')]")
public class SearchForm extends HtmlElement implements BlockWithSearchForm, Validateable<DesktopYaruMorda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//button[contains(@type, 'submit')]")
    private HtmlElement searchButton;

    @Override
    @Step("Check search form")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopYaruMorda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector()
                .check(
                        shouldSeeElementMatchingTo(this, hasAttribute(ACTION,
                                        equalTo(validator.getMorda().getSerpUrl().toString()))
                        )
                );

        return collector()
                .check(shouldSeeElement(this))
                .check(
                        searchFormCollector,
                        validateSearchInput(validator),
                        validateSearchButton(validator)
                );
    }

    @Step("Check search input")
    public HierarchicalErrorCollector validateSearchInput(Validator<? extends DesktopYaruMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("Check search button")
    public HierarchicalErrorCollector validateSearchButton(Validator<? extends DesktopYaruMorda> validator) {
        return collector()
                .check(shouldSeeElement(searchButton))
                .check(
                        shouldSeeElementMatchingTo(searchButton,
                                hasText(getTranslation(Dictionary.Home.Main.SEARCH, Language.RU)))
                );
    }

    public TextInput getSearchInput() {
        return searchInput;
    }

    public HtmlElement getLr() {
        return null;
    }

    public HtmlElement getSearchButton() {
        return searchButton;
    }

}
