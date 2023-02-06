package ru.yandex.autotests.morda.pages.desktop.tune.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithPlaces;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Common;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Places;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Region;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: asamar
 * Date: 15.08.16
 */
@Name("Настройки мест")
@FindBy(xpath = "//form[contains(@class, 'form')]")
public class TunePlaces extends HtmlElement implements Validateable<Morda<? extends TuneWithPlaces>> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h1")
    public HtmlElement title;

    @Name("Дом")
    @FindBy(xpath = ".//label[@class = 'places-options__title-line'][1]")
    public HtmlElement home;

    @Name("Работа")
    @FindBy(xpath = ".//label[@class = 'places-options__title-line'][2]")
    public HtmlElement work;

    @Name("Инпут дом")
    @FindBy(xpath = ".//input[@name = 'home']")
    public TextInput homeInput;

    @Name("Инпут работа")
    @FindBy(xpath = ".//input[@name = 'work']")
    public TextInput jobInput;

    @Name("Сохранить")
    @FindBy(xpath = ".//button[contains(@class, 'form__save')]")
    public HtmlElement saveButton;

    @Name("Саджест")
    @FindBy(xpath = "//li[contains(@class, 'b-autocomplete-item_type_geo')]")
    public List<HtmlElement> suggest;

    @Step("{0}")
    private HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                     Validator<? extends Morda<? extends TuneWithPlaces>> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title,
                                hasText(getTranslationSafely(Places.TITLE, validator.getMorda().getLanguage()))));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateHome(HtmlElement home,
                                                    Validator<? extends Morda<? extends TuneWithPlaces>> validator) {
        return collector()
                .check(shouldSeeElement(home))
                .check(
                        shouldSeeElementMatchingTo(home,
                                hasText(getTranslationSafely(Region.HOME, validator.getMorda().getLanguage()))));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateJob(HtmlElement work,
                                                   Validator<? extends Morda<? extends TuneWithPlaces>> validator) {
        return collector()
                .check(shouldSeeElement(work))
                .check(
                        shouldSeeElementMatchingTo(work,
                                hasText(getTranslationSafely(Region.WORK, validator.getMorda().getLanguage()))));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateHomeInput(TextInput homeInput,
                                                         Validator<? extends Morda<? extends TuneWithPlaces>> validator) {
        return collector()
                .check(shouldSeeElement(homeInput));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateJobInput(TextInput jobInput,
                                                        Validator<? extends Morda<? extends TuneWithPlaces>> validator) {
        return collector()
                .check(shouldSeeElement(jobInput));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSaveButton(HtmlElement saveButton,
                                                          Validator<? extends Morda<? extends TuneWithPlaces>> validator) {
        return collector()
                .check(shouldSeeElement(saveButton))
                .check(
                        shouldSeeElementMatchingTo(saveButton,
                                hasText(getTranslationSafely(Common.SAVE_BUTTON, validator.getMorda().getLanguage()))));
    }

    @Override
    @Step("Validate places")
    public HierarchicalErrorCollector validate(Validator<? extends Morda<? extends TuneWithPlaces>> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(title, validator),
                        validateHome(home, validator),
                        validateHomeInput(homeInput, validator),
                        validateJob(work, validator),
                        validateJobInput(jobInput, validator),
                        validateSaveButton(saveButton, validator)
                );
    }
}
