package ru.yandex.autotests.morda.pages.desktop.tune.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithAdv;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.SettingsCheckBox;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Adv;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Common;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: asamar
 * Date: 15.08.16
 */
@Name("Настройки рекламы")
@FindBy(xpath = "//form")
public class TuneAdv extends HtmlElement implements Validateable<Morda<? extends TuneWithAdv>> {
    @Name("Заголовок \"Настройка рекламы\"")
    @FindBy(xpath = ".//h1")
    public HtmlElement mainTitle;

    @Name("Подзаголовок \"Главная страница\"")
    @FindBy(xpath = ".//h2[1]")
    public HtmlElement mainPageTitle;

    @Name("Вопросик около \"Главная страница\"")
    @FindBy(xpath = ".//h2[1]//i[contains(@class, 'hint__icon_hover')]/parent::div")
    public HtmlElement mainPageHintButton;

    @Name("Чекбокс \"Показывать рекламу\"")
    @FindBy(xpath = ".//input[@name='yes_main_banner']/parent::span")
    public SettingsCheckBox advCheckBox;

    @Name("\"Показывать рекламу\"")
    @FindBy(xpath = ".//div[contains(@class, 'option_type_checkbox')][1]//label")
    public HtmlElement advLabel;

    @Name("Описание настройки \"Показывать рекламу\"")
    @FindBy(xpath = ".//div[contains(@class, 'option_type_checkbox')][1]//p")
    public HtmlElement advDescr;

    @Name("Подзаголовок \"Яндекс.Директ\"")
    @FindBy(xpath = ".//h2[2]")
    public HtmlElement directTitle;

    @Name("Вопросик около \"Яндекс.Директ\"")
    @FindBy(xpath = ".//h2[2]//i[contains(@class, 'hint__icon_hover')]/parent::div")
    public HtmlElement directHintButton;

    @Name("Чекбокс \"Учитывать мои интересы\"")
    @FindBy(xpath = ".//input[@name='yes_interest_ad']/parent::span")
    public SettingsCheckBox interestCheckBox;

    @Name("\"Учитывать мои интересы\"")
    @FindBy(xpath = ".//div[contains(@class, 'option_type_checkbox')][2]//label")
    public HtmlElement interestLabel;

    @Name("Описание настройки \"Учитывать мои интересы\"")
    @FindBy(xpath = ".//div[contains(@class, 'option_type_checkbox')][2]//p")
    public HtmlElement interestDescr;

    @Name("Чекбокс \"Учитывать мое местоположение\"")
    @FindBy(xpath = ".//input[@name='yes_geo_ad']/parent::span")
    public SettingsCheckBox geoCheckBox;

    @Name("\"Учитывать мое местоположение\"")
    @FindBy(xpath = ".//div[contains(@class, 'option_type_checkbox')][3]//label")
    public HtmlElement geoLabel;

    @Name("Описание настройки \"Учитывать мое местоположение\"")
    @FindBy(xpath = ".//div[contains(@class, 'option_type_checkbox')][3]//p")
    public HtmlElement geoDescr;

    @Name("Соглашение")
    @FindBy(xpath = ".//div[@class='agreement']")
    public HtmlElement agreement;

    @Name("Сохранить")
    @FindBy(xpath = ".//button[contains(@class, 'form__save')]")
    public HtmlElement saveButton;

    @Name("Подсказка главной страницы")
    @FindBy(xpath = "//div[@class = 'popup__content' and not(descendant::p)]")
    public HtmlElement mainPageHint;

    @Name("Подсказка директа")
    @FindBy(xpath = "//p//parent::div[@class = 'popup__content']")
    public HtmlElement directHint;


    @Step("Validate main page hint")
    public HierarchicalErrorCollector validateMainPageHint(Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(mainPageHint))
                .check(
                        shouldSeeElementMatchingTo(mainPageHint,
                                hasText(getTranslationSafely(Adv.MAIN_PAGE_HINT, validator.getMorda().getLanguage())))
                );
    }

    @Step("Validate direct hint")
    public HierarchicalErrorCollector validateDirectHint(Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(directHint))
                .check(
                        shouldSeeElementMatchingTo(directHint,
                                hasText(
                                        getTranslationSafely(Adv.DIRECT_HINT, validator.getMorda().getLanguage())
                                                .replaceAll("[\\]\\[]", "")
                                                .replaceAll("(?<=\\.)(?=\\S)", "\n")
                                )
                        )
                );
    }


    @Step("{0}")
    private HierarchicalErrorCollector validateMainTitle(HtmlElement mainTitle,
                                                         Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(mainTitle))
                .check(
                        shouldSeeElementMatchingTo(mainTitle,
                                hasText(getTranslationSafely(Adv.TITLE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateMainPage(HtmlElement mainPageTitle,
                                                        Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(mainPageTitle))
                .check(
                        shouldSeeElementMatchingTo(mainPageTitle,
                                hasText(getTranslationSafely(Adv.MAIN_PAGE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateAdvCheckBox(SettingsCheckBox advCheckBox,
                                                           Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(advCheckBox));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateAdvLabel(HtmlElement advLabel,
                                                        Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(advLabel))
                .check(
                        shouldSeeElementMatchingTo(advLabel,
                                hasText(getTranslationSafely(Adv.ADV_LABEL, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateAdvText(HtmlElement advDescr,
                                                       Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(advDescr))
                .check(
                        shouldSeeElementMatchingTo(advDescr,
                                hasText(getTranslationSafely(Adv.ADV_TEXT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateDirectTitle(HtmlElement directTitle,
                                                           Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(directTitle))
                .check(
                        shouldSeeElementMatchingTo(directTitle,
                                hasText(getTranslationSafely(Adv.DIRECT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateInterestCheckBox(SettingsCheckBox interestCheckBox,
                                                                Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(interestCheckBox));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateInterestsLabel(HtmlElement interestLabel,
                                                              Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(interestLabel))
                .check(
                        shouldSeeElementMatchingTo(interestLabel,
                                hasText(getTranslationSafely(Adv.INTERESTS_LABEL, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateInterestsText(HtmlElement interestDescr,
                                                             Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(interestDescr))
                .check(
                        shouldSeeElementMatchingTo(interestDescr,
                                hasText(getTranslationSafely(Adv.INTERESTS_TEXT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateGeoCheckBox(SettingsCheckBox geoCheckBox,
                                                           Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(geoCheckBox));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateGeoLabel(HtmlElement geoLabel,
                                                        Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(geoLabel))
                .check(
                        shouldSeeElementMatchingTo(geoLabel,
                                hasText(getTranslationSafely(Adv.GEO_LABEL, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateGeoDescr(HtmlElement geoDescr,
                                                        Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(geoDescr))
                .check(
                        shouldSeeElementMatchingTo(geoDescr,
                                hasText(getTranslationSafely(Adv.GEO_TEXT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateAgreement(HtmlElement agreement,
                                                         Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(agreement))
                .check(
                        shouldSeeElementMatchingTo(agreement,
                                hasText(getTranslationSafely(Adv.AGREEMENT, validator.getMorda().getLanguage()).replaceAll("[\\[\\]]", "")))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSaveButton(HtmlElement saveButton,
                                                          Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(saveButton))
                .check(
                        shouldSeeElementMatchingTo(saveButton,
                                hasText(getTranslationSafely(Common.SAVE_BUTTON, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateDirectHintButton(HtmlElement mainPageHintButton,
                                                                Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(mainPageHintButton));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateMainPageHintButton(HtmlElement directHintButton,
                                                                  Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(directHintButton));
    }


    @Override
    @Step("Validate adv block")
    public HierarchicalErrorCollector validate(Validator<? extends Morda<? extends TuneWithAdv>> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateMainTitle(mainTitle,validator),
                        validateMainPage(mainPageTitle, validator),
                        validateAdvCheckBox(advCheckBox, validator),
                        validateAdvLabel(advLabel, validator),
                        validateAdvText(advDescr, validator),
                        validateDirectTitle(directTitle, validator),
                        validateInterestCheckBox(interestCheckBox, validator),
                        validateInterestsLabel(interestLabel, validator),
                        validateInterestsText(interestDescr, validator),
                        validateGeoCheckBox(geoCheckBox, validator),
                        validateGeoLabel(geoLabel, validator),
                        validateGeoDescr(geoDescr, validator),
                        validateAgreement(agreement, validator),
                        validateSaveButton(saveButton, validator),
                        validateDirectHintButton(directHintButton, validator),
                        validateMainPageHintButton(mainPageHintButton, validator)
                );
    }
}
