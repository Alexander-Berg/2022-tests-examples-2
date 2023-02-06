package ru.yandex.autotests.tune.data.pages;

import io.qameta.htmlelements.WebPage;
import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.HtmlElement;
import org.openqa.selenium.JavascriptExecutor;
import ru.yandex.autotests.morda.beans.cleanvars.geo.GeoLocation;
import ru.yandex.autotests.morda.data.validation.Validateable;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.tune.data.element.CheckBox;
import ru.yandex.autotests.tune.data.element.Input;
import ru.yandex.autotests.tune.data.element.InputSuggest;
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
 * Date: 14.12.16
 */
public interface GeoPage extends WebPage, Validateable<TuneMorda> {

    @FindBy("//h1")
    HtmlElement title();

    @FindBy("//button[contains(@class, 'geo-map__promo-locate')]")
    HtmlElement findMeButton();

    @FindBy("//span[contains(@class, 'city__input')]")
    Input cityInput();

    @FindBy("//span[contains(@class, 'checkbox_geo_auto')]")
    CheckBox automaticaly();

    @FindBy("//div[contains(@class, 'city__after')]")
    HtmlElement cityAfter();

    @FindBy("//div[@class = 'tune-footer__logo']")
    Logo logo();

    @FindBy("//button[contains(@class, 'form__save')]")
    HtmlElement saveButton();

    @FindBy("//div[@class = 'popup__content']")
    InputSuggest suggest();

    @Override
    @Step("Open common settings page")
    default void open(String baseUrl) {
        getWrappedDriver().get(fromUri(baseUrl).path("geo").build().toString());
    }

    @Override
    @Step("Validate geo page")
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(validateTitle(title(), validator))
                .check(validateFindMe(findMeButton(), validator))
                .check(validateCityInput(cityInput(), validator))
                .check(validateAutomaticaly(automaticaly(), validator))
                .check(validateCityAfter(cityAfter(), validator))
                .check(logo().validate(validator));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                     Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> title
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Tabs.GEO, validator.getMorda().getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateFindMe(HtmlElement findMe,
                                                      Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> findMe
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Geo.LOCATE, validator.getMorda().getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateCityAfter(HtmlElement cityAfter,
                                                         Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> cityAfter
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Geo.FOOTER, validator.getMorda().getLanguage())
                                        .replaceAll("&nbsp;"," ")
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateAutomaticaly(CheckBox automaticaly,
                                                            Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> automaticaly.label()
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Geo.AUTO, validator.getMorda().getLanguage())
                        ))
                )
                .check(() -> automaticaly.span()
                        .should(displayed())
                );
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateCityInput(Input cityInput,
                                                         Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> cityInput.label()
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Geo.CITY, validator.getMorda().getLanguage()).toUpperCase()
                        ))
                )
                .check(() -> cityInput.inputBox()
                        .should(displayed())
                );
    }

    @Step("Set {0} coordinates")
    default void setGeoLocation(GeoLocation geoLocation){
        ((JavascriptExecutor) getWrappedDriver())
                .executeScript("x = { coords: { latitude: " +
                        geoLocation.getLat() +
                        ", longitude: " +
                        geoLocation.getLon() +
                        ", accuracy: 1444 }}; " +
                        "window.navigator.geolocation.getCurrentPosition = function(success){success(x)}");
        ((JavascriptExecutor) getWrappedDriver())
                .executeScript("window.navigator.geolocation.getCurrentPosition(function(ok){console.log(ok)})");
    }

    @Step
    default void findMeClick() {
        findMeButton().should(displayed()).click();
    }

    @Step("Get suggest item {1}")
    default InputSuggest.Item getSuggestItem(String city) {
        return suggest().items().stream()
                .filter(e -> e.city().getText().startsWith(city))
                .findFirst()
                .orElseThrow(() -> new AssertionError("В саджесте нет нужного города"));
    }


}
