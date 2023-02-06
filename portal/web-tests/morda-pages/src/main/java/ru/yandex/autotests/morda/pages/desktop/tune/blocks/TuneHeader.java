package ru.yandex.autotests.morda.pages.desktop.tune.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Common;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Tabs;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: asamar
 * Date: 15.08.16
 */
@Name("Хедер")
@FindBy(xpath = "//div[@class = 'tune-header']")
public class TuneHeader extends HtmlElement implements Validateable<Morda<? extends PageWithHeader<TuneHeader>>> {

    @Name("Местоположение")
    @FindBy(xpath = ".//a[@data-statlog = 'tabs.geo']")
    public HtmlElement geoTab;

    @Name("Мои места")
    @FindBy(xpath = ".//a[@data-statlog = 'tabs.places']")
    public HtmlElement placesTab;

    @Name("Язык")
    @FindBy(xpath = ".//a[@data-statlog = 'tabs.lang']")
    public HtmlElement langTab;

    @Name("Поиск")
    @FindBy(xpath = ".//a[@data-statlog = 'tabs.search']")
    public HtmlElement searchTab;

    @Name("Реклама")
    @FindBy(xpath = ".//a[@data-statlog = 'tabs.adv']")
    public HtmlElement advTab;

    @Name("Паспорт")
    @FindBy(xpath = ".//a[@data-statlog = 'tabs.passport']")
    public HtmlElement passportTab;

    @Name("Лого")
    @FindBy(xpath = ".//a[contains(@class, 'logo')]")
    public HtmlElement logo;

    @Name("Войти")
    @FindBy(xpath = ".//a[@data-statlog = 'user.login']")
    public HtmlElement logIn;

    public AuthorizedToggler authorizedToggler;

    @Name("Кнопка показа домика")
    @FindBy(xpath = ".//a[contains(@class, 'personal__toggler')]")
    public static class AuthorizedToggler extends HtmlElement {

        @Name("Имя пользователя")
        @FindBy(xpath = ".//span[@class = 'user__name']")
        public HtmlElement name;

        @Name("Иконка")
        @FindBy(xpath = ".//span[@class = 'user__icon']")
        public HtmlElement icon;

        @Step("Validate autorized header")
        public HierarchicalErrorCollector validate(
                Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {

            return collector()
                    .check(shouldSeeElement(this))
                    .check(
                            validateUserName(name, validator),
                            validateUserIcon(icon, validator)
                    );
        }

        @Step("{0}")
        public HierarchicalErrorCollector validateUserName(HtmlElement name,
                                                           Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {

            return collector()
                    .check(shouldSeeElement(name))
                    .check(
                            shouldSeeElementMatchingTo(name,
                                    hasText(not(isEmptyOrNullString())))
                    );
        }

        @Step("{0}")
        public HierarchicalErrorCollector validateUserIcon(HtmlElement icon,
                                                           Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {

            return collector()
                    .check(shouldSeeElement(icon));
        }
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateGeoTab(HtmlElement geoTab,
                                                      Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        return collector()
                .check(shouldSeeElement(geoTab))
                .check(shouldSeeElementMatchingTo(geoTab,
                                hasText(getTranslationSafely(Tabs.GEO, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validatePlacesTab(HtmlElement placesTab,
                                                         Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        return collector()
                .check(shouldSeeElement(placesTab))
                .check(shouldSeeElementMatchingTo(placesTab,
                                hasText(getTranslationSafely(Tabs.PLACES, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateLanguageTab(HtmlElement langTab,
                                                           Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        return collector()
                .check(shouldSeeElement(langTab))
                .check(shouldSeeElementMatchingTo(langTab,
                                hasText(getTranslationSafely(Tabs.LANG, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateSearchTab(HtmlElement searchTab,
                                                         Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        return collector()
                .check(shouldSeeElement(searchTab))
                .check(shouldSeeElementMatchingTo(searchTab,
                                hasText(getTranslationSafely(Tabs.SEARCH, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateAdvTab(HtmlElement advTab,
                                                      Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        return collector()
                .check(shouldSeeElement(advTab))
                .check(shouldSeeElementMatchingTo(advTab,
                                hasText(getTranslationSafely(Tabs.ADV, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validatePassportTab(HtmlElement passportTab,
                                                           Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        return collector()
                .check(shouldSeeElement(passportTab))
                .check(shouldSeeElementMatchingTo(passportTab,
                                hasText(getTranslationSafely(Tabs.PASSPORT, validator.getMorda().getLanguage())))
                );
    }

    @Step("Login")
    private HierarchicalErrorCollector validateLogIn(
            Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {

        return validator.getUser() == null ?
                collector()
                        .check(shouldSeeElement(logIn))
                        .check(shouldSeeElementMatchingTo(logIn,
                                        hasText(getTranslationSafely(Common.LOGIN, validator.getMorda().getLanguage())))
                        ) :
                collector()
                        .check(authorizedToggler.validate(validator));

    }

    @Step("{0}")
    private HierarchicalErrorCollector validateLogo(HtmlElement logo,
                                                    Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        return collector()
                .check(shouldSeeElement(logo));
    }

    @Override
    @Step("Validate header")
    public HierarchicalErrorCollector validate(Validator<? extends Morda<? extends PageWithHeader<TuneHeader>>> validator) {
        MordaType type = validator.getMorda().getMordaType();
        HierarchicalErrorCollector collector = collector();

        switch (type) {
            case TUNE_MAIN:
                collector
                        .check(shouldSeeElement(this))
                        .check(
                                validateGeoTab(geoTab, validator),
                                validatePlacesTab(placesTab, validator),
                                validateLanguageTab(langTab, validator),
                                validateSearchTab(searchTab, validator),
                                validateAdvTab(advTab, validator),
                                validatePassportTab(passportTab, validator),
                                validateLogIn(validator),
                                validateLogo(logo, validator)
                        );
                break;

            case TUNE_COM:
                collector
                        .check(shouldSeeElement(this))
                        .check(
                                validateSearchTab(searchTab, validator),
                                validatePassportTab(passportTab, validator),
                                validateLogIn(validator),
                                validateLogo(logo, validator)
                        );
                break;

            case TUNE_COM_TR:
                collector
                        .check(shouldSeeElement(this))
                        .check(
                                validateGeoTab(geoTab, validator),
                                validatePlacesTab(placesTab, validator),
                                validateSearchTab(searchTab, validator),
                                validatePassportTab(passportTab, validator),
                                validateLogIn(validator),
                                validateLogo(logo, validator)
                        );
                break;
        }

        return collector;
    }
}
