package ru.yandex.autotests.morda.pages.desktop.com404.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.ACTION;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.SEARCH;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 06.10.2015.
 */
@Name("Поисковая форма")
@FindBy(xpath = "//form[contains(@class, 'suggest2-form')]")
public class SearchForm  extends HtmlElement implements BlockWithSearchForm, Validateable<Com404Morda> {

    @Name("Поисковая строка")
    @FindBy(xpath = ".//input[@name='text']")
    private TextInput searchInput;

    @Name("Иконка виртуальной клавиатуры")
    @FindBy(xpath = ".//i[contains(@class, 'b-ico keyboard-loader__icon b-ico-kbd')]")
    private HtmlElement virtualKeyboardButton;

    @Name("Кнопка \"Найти\"")
    @FindBy(xpath = ".//button[contains(@type, 'submit')]")
    private HtmlElement searchButton;

    @Override
    @Step("Check search form")
    public HierarchicalErrorCollector validate(Validator<? extends Com404Morda> validator) {
        HierarchicalErrorCollector searchFormCollector = collector()
                .check(shouldSeeElement(this))
                .check(shouldSeeElementMatchingTo(this,
                        hasAttribute(ACTION, equalTo("https://yandex.com/search/"))));

        return searchFormCollector
                .check(
                        validateSearchInput(searchInput, validator),
                        validateSearchButton(searchButton, validator),
                        validateVirtualkeyboardButton(virtualKeyboardButton, validator)
                );

    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateSearchInput(TextInput searchInput,
                                                                 Validator<? extends Com404Morda> validator) {
        return collector()
                .check(shouldSeeElement(searchInput));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateSearchButton(HtmlElement searchButton,
                                                                  Validator<? extends Com404Morda> validator) {
        return collector()
                .check(shouldSeeElement(searchButton))
                .check(
                        shouldSeeElementMatchingTo(searchButton,
                                hasText(getTranslation(SEARCH, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateVirtualkeyboardButton(HtmlElement virtualKeyboardButton,
                                                                           Validator<? extends Com404Morda> validator){
        return collector()
                .check(shouldSeeElement(virtualKeyboardButton));
    }

    public TextInput getSearchInput() {
        return searchInput;
    }

    public HtmlElement getVirtualKeyboardButton(){
        return virtualKeyboardButton;
    }

    public HtmlElement getLr() {
        return null;
    }

    public HtmlElement getSearchButton() {
        return searchButton;
    }
}
