package ru.yandex.autotests.morda.pages.desktop.tune.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithGeo;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.SettingsCheckBox;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Common;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Geo;
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
@Name("Настройки местоположения")
@FindBy(xpath = "//form[contains(@class, 'form_type_geo')]")
public class TuneGeo extends HtmlElement implements Validateable<Morda<? extends TuneWithGeo>> {

    @Name("Заголовок \"Уточнить местоположение\"")
    @FindBy(xpath = ".//h1")
    public HtmlElement title;

    @Name("Описание на карте")
    @FindBy(xpath = ".//div[@class='geo-map__text']")
    public HtmlElement descr;

    @Name("Кнопка \"Найти меня\"")
    @FindBy(xpath = ".//button[contains(@class, 'geo-map__promo-locate')]")
    public HtmlElement locateButton;

    @Name("Город")
    @FindBy(xpath = ".//label[@class='city__title']")
    public HtmlElement cityTitle;

    @Name("Инпут")
    @FindBy(xpath = ".//input[contains(@class, 'input__control')]")
    public TextInput cityInput;

    @Name("Чекбокс \"Определять автоматически\"")
    @FindBy(xpath = ".//input[@class= 'checkbox__control']/parent::span")
    public SettingsCheckBox autoCheckBox;

    @Name("Определять автоматически")
    @FindBy(xpath = ".//label[@class = 'checkbox__label']")
    public HtmlElement autoLabel;

    @Name("Кнопка \"Сохранить\"")
    @FindBy(xpath = ".//button[contains(@class, 'form__save')]")
    public HtmlElement saveButton;

    @Name("Саджест")
    @FindBy(xpath = "//div[@class = 'popup__content']")
    public GeoSuggest suggest;

    public static class GeoSuggest extends HtmlElement {

        public class SuggestItems extends HtmlElement{

            @Name("Город")
            @FindBy(xpath = ".//div[@class = 'b-autocomplete-item__reg']")
            public HtmlElement city;

            @Name("Регион")
            @FindBy(xpath = ".//div[@class = 'b-autocomplete-item__details']")
            public HtmlElement region;
        }

        @Name("Саджест")
        @FindBy(xpath = ".//li[contains(@class, 'b-autocomplete-item_type_geo')]")
        public List<SuggestItems> items;

    }



    @Step("{0}")
    private HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                     Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title,
                                hasText(getTranslationSafely(Geo.PROMO_TITLE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateDescr(HtmlElement descr,
                                                     Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(descr))
                .check(
                        shouldSeeElementMatchingTo(descr,
                                hasText(getTranslationSafely(Geo.PROMO_TEXT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateLocate(HtmlElement locateButton,
                                                      Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(locateButton))
                .check(
                        shouldSeeElementMatchingTo(locateButton,
                                hasText(getTranslationSafely(Geo.LOCATE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateCity(HtmlElement cityTitle,
                                                    Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(cityTitle))
                .check(
                        shouldSeeElementMatchingTo(cityTitle,
                                hasText(getTranslationSafely(Geo.CITY, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateCityInput(TextInput cityInput,
                                                         Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(cityInput));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateAutoCheckBox(SettingsCheckBox autoCheckBox,
                                                            Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(autoCheckBox));

    }

    @Step("{0}")
    private HierarchicalErrorCollector validateAutoLabel(HtmlElement autoLabel,
                                                         Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(autoLabel))
                .check(
                        shouldSeeElementMatchingTo(autoLabel,
                                hasText(getTranslationSafely(Geo.AUTO, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSaveButton(HtmlElement saveButton,
                                                          Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(saveButton))
                .check(
                        shouldSeeElementMatchingTo(saveButton,
                                hasText(getTranslationSafely(Common.SAVE_BUTTON, validator.getMorda().getLanguage())))
                );
    }

    @Override
    @Step("Validate geo")
    public HierarchicalErrorCollector validate(Validator<? extends Morda<? extends TuneWithGeo>> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(title, validator),
                        validateDescr(descr, validator),
                        validateLocate(locateButton, validator),
                        validateCity(cityTitle, validator),
                        validateCityInput(cityInput, validator),
                        validateAutoCheckBox(autoCheckBox, validator),
                        validateAutoLabel(autoLabel, validator),
                        validateSaveButton(saveButton, validator)
                );
    }
}
