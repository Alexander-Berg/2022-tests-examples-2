package ru.yandex.autotests.morda.pages.desktop.tune.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithSearch;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.SettingsCheckBox;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Common;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Suggest;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: asamar
 * Date: 15.08.16
 */
@Name("Настройки поиска")
@FindBy(xpath = "//form[contains(@class, 'form')]")
public class TuneSearch extends HtmlElement implements Validateable<Morda<? extends TuneWithSearch>> {

    @Name("Заголовок \"Настройка поиска\"")
    @FindBy(xpath = ".//h1")
    public HtmlElement mainTitle;

    @Name("Подзаголовок \"Поисковые подсказки\"")
    @FindBy(xpath = ".//h2")
    public HtmlElement suggestTitle;

    @Name("Чекбокс \"Показывать частые запросы\"")
    @FindBy(xpath = ".//input[@name = 'nahodki']/parent::span")
    public SettingsCheckBox requestsCheckBox;

    @Name("Показывать частые запросы")
    @FindBy(xpath = ".//input[@name = 'nahodki']/following::label[1]")
    public HtmlElement requestsLabel;

    @Name("Описание \"Показывать частые запросы\"")
    @FindBy(xpath = ".//input[@name = 'nahodki']/following::div[1]/p[1]")
    public HtmlElement requestsDescr;

    @Name("Условие показа частых запросов")
    @FindBy(xpath = ".//input[@name = 'nahodki']/following::div[1]/p[2]")
    public HtmlElement requestHint;

    @Name("Чекбокс \"Показывать сайты, на которые часто заходите\"")
    @FindBy(xpath = ".//input[@name = 'favorite_sites']/parent::span")
    public SettingsCheckBox sitesCheckBox;

    @Name("Показывать сайты, на которые часто заходите")
    @FindBy(xpath = ".//input[@name = 'favorite_sites']/following::label")
    public HtmlElement sitesLabel;

    @Name("Описание \"Показывать сайты, на которые часто заходите\"")
    @FindBy(xpath = ".//input[@name = 'favorite_sites']/following::div[1]")
    public HtmlElement sitesDescr;

    @Name("Результаты поиска")
    @FindBy(xpath = ".//a[@data-statlog = 'serp_settings']")
    public HtmlElement searchResults;

    @Name("Описание результатов поиска")
    @FindBy(xpath = ".//a[@data-statlog = 'serp_settings']/following::div[@class = 'option__footer']")
    public HtmlElement searchDescr;

    @Name("Мои находки")
    @FindBy(xpath = ".//a[@data-statlog = 'nahodki']")
    public HtmlElement myFindings;

    @Name("Описание моих находок")
    @FindBy(xpath = ".//a[@data-statlog = 'nahodki']/following::div[@class = 'option__footer']")
    public HtmlElement myFindingsDescr;

    @Name("Сохранить")
    @FindBy(xpath = ".//button[contains(@class, 'form__save')]")
    public HtmlElement saveButton;

    @Step("{0}")
    private HierarchicalErrorCollector validateMainTitle(HtmlElement mainTitle,
                                                         Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(mainTitle))
                .check(
                        shouldSeeElementMatchingTo(mainTitle,
                                hasText(getTranslationSafely(Suggest.SEARCH_TITLE,
                                        validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSuggestTitle(HtmlElement suggestTitle,
                                                            Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(suggestTitle))
                .check(
                        shouldSeeElementMatchingTo(suggestTitle,
                                hasText(getTranslationSafely(Suggest.SEARCH_SUGGEST_TITLE2,
                                        validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateRequestCheckBox(SettingsCheckBox requestsCheckBox,
                                                               Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(requestsCheckBox));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateRequestLabel(HtmlElement requestsLabel,
                                                            Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(requestsLabel))
                .check(
                        shouldSeeElementMatchingTo(requestsLabel,
                                hasText(getTranslationSafely(Suggest.FAVOURITE_REQ_LABEL, validator.getMorda().getLanguage()))));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateRequestDescr(HtmlElement requestsDescr,
                                                            Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(requestsDescr))
                .check(
                        shouldSeeElementMatchingTo(requestsDescr,
                                hasText(getTranslationSafely(Suggest.FAVOURITE_REQ_TEXT, validator.getMorda().getLanguage()))));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateRequestHint(HtmlElement requestHint,
                                                           Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(requestHint))
                .check(
                        shouldSeeElementMatchingTo(requestHint,
                                hasText(getTranslationSafely(Suggest.FAVOURITE_REQ_HINT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSitesCheckBox(SettingsCheckBox sitesCheckBox,
                                                             Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(sitesCheckBox));
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSitesLabel(HtmlElement sitesLabel,
                                                          Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(sitesLabel))
                .check(
                        shouldSeeElementMatchingTo(sitesLabel,
                                hasText(getTranslationSafely(Suggest.FAVOURITE_SITES_LABEL, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSitesDescr(HtmlElement sitesDescr,
                                                          Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(sitesDescr))
                .check(
                        shouldSeeElementMatchingTo(sitesDescr,
                                hasText(getTranslationSafely(Suggest.FAVOURITE_SITES_TEXT, validator.getMorda().getLanguage()).trim()))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSearchResults(HtmlElement searchResults,
                                                             Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(searchResults))
                .check(
                        shouldSeeElementMatchingTo(searchResults,
                                hasText(getTranslationSafely(Suggest.SERP_TITLE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSearchDescr(HtmlElement searchDescr,
                                                           Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(searchDescr))
                .check(
                        shouldSeeElementMatchingTo(searchDescr,
                                hasText(getTranslationSafely(Suggest.SERP_TEXT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateMyFindings(HtmlElement myFindings,
                                                          Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(myFindings))
                .check(
                        shouldSeeElementMatchingTo(myFindings,
                                hasText(getTranslationSafely(Suggest.NAHODKI_TITLE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateMyFindingsDescr(HtmlElement myFindingsDescr,
                                                               Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(myFindingsDescr))
                .check(
                        shouldSeeElementMatchingTo(myFindingsDescr,
                                hasText(getTranslationSafely(Suggest.NAHODKI_TEXT, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSaveButton(HtmlElement saveButton,
                                                          Validator<? extends Morda<? extends TuneWithSearch>> validator) {
        return collector()
                .check(shouldSeeElement(saveButton))
                .check(
                        shouldSeeElementMatchingTo(saveButton,
                                hasText(getTranslationSafely(Common.SAVE_BUTTON, validator.getMorda().getLanguage()))));
    }

    @Override
    @Step("Validate search")
    public HierarchicalErrorCollector validate(Validator<? extends Morda<? extends TuneWithSearch>> validator) {

        MordaType type = validator.getMorda().getMordaType();
        HierarchicalErrorCollector collector = collector();

        switch (type) {
            case TUNE_MAIN:
                collector
                        .check(shouldSeeElement(this))
                        .check(
                                validateMainTitle(mainTitle, validator),
                                validateSuggestTitle(suggestTitle, validator),

                                validateRequestCheckBox(requestsCheckBox, validator),
                                validateRequestLabel(requestsLabel, validator),
                                validateRequestDescr(requestsDescr, validator),
                                validateRequestHint(requestHint, validator),

                                validateSitesCheckBox(sitesCheckBox, validator),
                                validateSitesLabel(sitesLabel, validator),
                                validateSitesDescr(sitesDescr, validator),

                                validateSearchResults(searchResults, validator),
                                validateSearchDescr(searchDescr, validator),

//                                validateMyFindings(myFindings, validator),
//                                validateMyFindingsDescr(myFindingsDescr, validator),

                                validateSaveButton(saveButton, validator)
                        );
                break;

            case TUNE_COM:
                collector
                        .check(shouldSeeElement(this))
                        .check(
                                validateMainTitle(mainTitle, validator),
                                validateSuggestTitle(suggestTitle, validator),

                                validateSitesCheckBox(sitesCheckBox, validator),
                                validateSitesLabel(sitesLabel, validator),
                                validateSitesDescr(sitesDescr, validator),

                                validateSearchResults(searchResults, validator),
                                validateSearchDescr(searchDescr, validator),

                                validateSaveButton(saveButton, validator)
                        );
                break;

            case TUNE_COM_TR:
                collector
                        .check(shouldSeeElement(this))
                        .check(
                                validateMainTitle(mainTitle, validator),
                                validateSuggestTitle(suggestTitle, validator),

                                validateRequestCheckBox(requestsCheckBox, validator),
                                validateRequestLabel(requestsLabel, validator),
                                validateRequestDescr(requestsDescr, validator),
                                validateRequestHint(requestHint, validator),

                                validateSitesCheckBox(sitesCheckBox, validator),
                                validateSitesLabel(sitesLabel, validator),
                                validateSitesDescr(sitesDescr, validator),

                                validateSearchResults(searchResults, validator),
                                validateSearchDescr(searchDescr, validator),

                                validateSaveButton(saveButton, validator)
                        );
                break;
        }
        return collector;
    }
}
