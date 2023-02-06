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
import static javax.ws.rs.core.UriBuilder.fromUri;
import static ru.yandex.autotests.morda.data.TankerManager.getSafely;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_TUNE;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.qatools.htmlelements.matchers.common.HasTextMatcher.hasText;

/**
 * User: asamar
 * Date: 12.12.16
 */
public interface AdvPage extends WebPage, Validateable<TuneMorda> {

    @FindBy("//h1")
    HtmlElement title();

    @FindBy("//li/span[.//input[@name = 'yes_main_banner']]")
    CheckBox showAdv();

    @FindBy("//li/span[.//input[@name = 'yes_interest_ad']]")
    CheckBox myInterests();

    @FindBy("//li/span[.//input[@name = 'yes_geo_ad']]")
    CheckBox myLocation();

    @FindBy("//div[@class = 'tune-footer__logo']")
    Logo logo();

    @FindBy("//button[contains(@class, 'form__save')]")
    HtmlElement saveButton();

    @FindBy("//a[contains(@class, 'tune-header__back')]")
    HtmlElement returnBack();

    @Override
    @Step("Open adv page")
    default void open(String baseUrl) {
        getWrappedDriver().get(fromUri(baseUrl).path("adv").build().toString());
    }

    @Override
    @Step("Validate adv page")
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(validateTitle(title(), validator))
                .check(logo().validate(validator))
                .check(validateShowAdv(showAdv(), validator))
                .check(validateMyInterests(myInterests(), validator))
                .check(validateMyLocation(myLocation(), validator));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateShowAdv(CheckBox showAdv,
                                                       Validator<? extends TuneMorda> validator) {
        TuneMorda<?> morda = validator.getMorda();
        if (morda.getMordaType() != TOUCH_TUNE) return collector();

        return collector()
                .check(() -> showAdv.should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Adv.ADV_LABEL, morda.getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateMyInterests(CheckBox myInterests,
                                                           Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> myInterests
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Adv.INTERESTS_LABEL, validator.getMorda().getLanguage())
                        )));

    }

    @Step("{0}")
    default HierarchicalErrorCollector validateMyLocation(CheckBox myLocation,
                                                          Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> myLocation
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Adv.GEO_LABEL, validator.getMorda().getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                     Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> title
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Tabs.ADV, validator.getMorda().getLanguage())
                        )));
    }

    @Step("Disable location settings")
    default void disableLocation() {
        myLocation().should(displayed()).unCheck();
        saveButton().waitUntil(displayed()).click();
    }

    @Step("Disable interests settings")
    default void disableInterests() {
        myInterests().should(displayed()).unCheck();
        saveButton().waitUntil(displayed()).click();
    }

    @Step("Disable adv settings")
    default void disableAdv() {
        showAdv().should(displayed()).unCheck();
        saveButton().waitUntil(displayed()).click();
    }

}
