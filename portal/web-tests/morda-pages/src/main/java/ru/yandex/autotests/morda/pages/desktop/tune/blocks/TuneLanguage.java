package ru.yandex.autotests.morda.pages.desktop.tune.blocks;

import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithLang;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.SettingsSelect;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Common;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Lang;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.element.Select;

import java.util.List;
import java.util.stream.IntStream;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: asamar
 * Date: 15.08.16
 */
@Name("Настройки языка")
@FindBy(xpath = "//div[contains(@class, 'page-views')]")
public class TuneLanguage extends HtmlElement implements Validateable<Morda<? extends TuneWithLang>> {

    @Name("Селект языка")
    @FindBy(xpath = "//div[contains(@class, 'option__select')]")
    public SettingsSelect langSelect;

    @Name("Заголовок")
    @FindBy(xpath = ".//h1")
    public HtmlElement langTitle;

    @Name("Выпадушка языка")
    @FindBy(xpath = ".//button[contains(@class, 'button_arrow_down')]")
    public HtmlElement langDropDown;

    @Name("Описание настройки")
    @FindBy(xpath = ".//div[@class = 'option__aside']")
    public HtmlElement description;

    @Name("Сохранить")
    @FindBy(xpath = ".//button[contains(@class, 'form__save')]")
    public HtmlElement saveButton;


    @Step("Select lang by value {0}")
    public void selectLangByValue(String value) {
        Select select = langSelect.getSelect();
        List<WebElement> options = select.getOptions();

        int index = IntStream.range(0, options.size())
                .filter(i -> value.equals(options.get(i).getAttribute("value")))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("Some shit happened"));
        langSelect.button.click();
        langSelect.popup.items.get(index).click();
    }


    @Step("{0}")
    private HierarchicalErrorCollector validateTitle(HtmlElement langTitle,
                                                     Validator<? extends Morda<? extends TuneWithLang>> validator) {
        return collector()
                .check(shouldSeeElement(langTitle))
                .check(
                        shouldSeeElementMatchingTo(langTitle,
                                hasText(getTranslationSafely(Lang.TITLE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateDescr(HtmlElement description,
                                                     Validator<? extends Morda<? extends TuneWithLang>> validator) {
        return collector()
                .check(shouldSeeElement(description))
                .check(
                        shouldSeeElementMatchingTo(description,
                                hasText(getTranslationSafely(Lang.HINT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSaveButton(HtmlElement saveButton,
                                                          Validator<? extends Morda<? extends TuneWithLang>> validator) {
        return collector()
                .check(shouldSeeElement(saveButton))
                .check(
                        shouldSeeElementMatchingTo(saveButton,
                                hasText(getTranslationSafely(Common.SAVE_BUTTON, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateLangDropDown(HtmlElement langDropDown,
                                                            Validator<? extends Morda<? extends TuneWithLang>> validator) {
        Language lang = validator.getMorda().getLanguage();
        return collector()
                .check(shouldSeeElement(langDropDown))
                .check(
                        shouldSeeElementMatchingTo(langDropDown,
                                hasText(getTranslationSafely("tune", "lang", lang.getValue(), lang)))
                );
    }

    @Override
    @Step("Validate language")
    public HierarchicalErrorCollector validate(Validator<? extends Morda<? extends TuneWithLang>> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(langTitle, validator),
                        validateDescr(description, validator),
                        validateSaveButton(saveButton, validator),
                        validateLangDropDown(langDropDown, validator)
                );
    }
}
