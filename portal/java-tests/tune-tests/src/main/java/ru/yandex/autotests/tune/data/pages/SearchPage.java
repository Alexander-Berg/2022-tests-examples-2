package ru.yandex.autotests.tune.data.pages;

import io.qameta.htmlelements.WebPage;
import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.HtmlElement;
import ru.yandex.autotests.morda.data.validation.Validateable;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.tune.data.element.CheckBox;
import ru.yandex.autotests.tune.data.element.Logo;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;

import static io.qameta.htmlelements.matcher.DisplayedMatcher.displayed;
import static io.qameta.htmlelements.matcher.HasTextMatcher.hasText;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static ru.yandex.autotests.morda.data.TankerManager.getSafely;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: asamar
 * Date: 13.12.16
 */
public interface SearchPage extends WebPage, Validateable<TuneMorda>{

    @FindBy("//h1")
    HtmlElement title();

    @FindBy("//li[1]/span")
    CheckBox favouriteRequests();

    @FindBy("//li[2]/span")
    CheckBox newWindow();

    @FindBy("//li[3]/span")
    CheckBox familySearch();

    @FindBy("//div[@class = 'tune-footer__logo']")
    Logo logo();

    @FindBy("//button[contains(@class, 'form__save')]")
    HtmlElement saveButton();

    @FindBy("//a[contains(@class, 'tune-header__back')]")
    HtmlElement returnBack();

    @Override
    @Step("Open search page")
    default void open(String baseUrl) {
        getWrappedDriver().get(fromUri(baseUrl).path("search").build().toString());
    }

    @Override
    @Step("Validate search page")
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(logo().validate(validator))
                .check(validateTitle(title(), validator))
                .check(validateFavouriteRequests(favouriteRequests(), validator))
                .check(validateNewWindow(newWindow(), validator))
                .check(validateFamilySearch(familySearch(), validator));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                     Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> title
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Tabs.SEARCH, validator.getMorda().getLanguage())
                        )));
    }


    @Step("{0}")
    default HierarchicalErrorCollector validateFavouriteRequests(CheckBox favouriteRequests,
                                                     Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> favouriteRequests
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Suggest.FAVOURITE_REQ_LABEL, validator.getMorda().getLanguage())
                        )));
    }


    @Step("{0}")
    default HierarchicalErrorCollector validateNewWindow(CheckBox newWindow,
                                                     Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> newWindow
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Suggest.NEW_WINDOW, validator.getMorda().getLanguage())
                                .replace("&nbsp;"," ")
                        )));
    }


    @Step("{0}")
    default HierarchicalErrorCollector validateFamilySearch(CheckBox familySearch,
                                                     Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> familySearch
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Suggest.FAMILY_SEARCH, validator.getMorda().getLanguage())
                        )));
    }

    @Step()
    default void checkFamilySearch() {
        familySearch().should(displayed()).check();
        saveButton().should(displayed()).click();
    }

    @Step()
    default void checkNewWindow() {
        newWindow().should(displayed()).check();
        saveButton().should(displayed()).click();

    }

    @Step()
    default void unCheckNewWindow() {
        newWindow().should(displayed()).unCheck();
        saveButton().should(displayed()).click();
    }

    @Step()
    default void checkFavouriteReq() {
        favouriteRequests().should(displayed()).check();
        saveButton().should(displayed()).click();
    }

}
