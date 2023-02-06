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
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_TUNE;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: asamar
 * Date: 01.12.16
 */
public interface CommonSettingsPage extends WebPage, Validateable<TuneMorda> {

    @FindBy("//h1")
    HtmlElement title();

    @FindBy("//li/span[.//input[@name = 'mobile_version']]")
    CheckBox mobVersionSites();

    @FindBy("//li/span[.//input[@name = 'yes_app_by_links']]")
    CheckBox openLiks();

    @FindBy("//li/span[.//input[@name = 'yes_mtd']]")
    CheckBox themeOnMain();

    @FindBy("//div[@class = 'tune-footer__logo']")
    Logo logo();

    @FindBy("//button[contains(@class, 'form__save')]")
    HtmlElement saveButton();

    @FindBy("//a[contains(@class, 'tune-header__back')]")
    HtmlElement returnBack();

    @Override
    @Step("Open common settings page")
    default void open(String baseUrl) {
        getWrappedDriver().get(fromUri(baseUrl).path("common").build().toString());
    }

    @Step("Validate common settings page")
    @Override
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(validateTitle(title(), validator))
                .check(logo().validate(validator))
                .check(validateMobVersionSites(mobVersionSites(), validator))
                .check(validateOpenLinks(openLiks(), validator))
                .check(validateThemeOnMain(themeOnMain(), validator));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> title
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Tabs.COMMON, validator.getMorda().getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateMobVersionSites(CheckBox mobVersionSites,
                                                               Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> mobVersionSites
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Common.MOBILE_VERSION, validator.getMorda().getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateOpenLinks(CheckBox openLinks,
                                                         Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> openLinks
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Mainpage.OPEN_IN_APP,
                                        validator.getMorda().getLanguage()).replace("&nbsp;", " ")
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateThemeOnMain(CheckBox themeOnMain,
                                                           Validator<? extends TuneMorda> validator) {
        TuneMorda<?> morda = validator.getMorda();

        if (morda.getMordaType() != TOUCH_TUNE) return collector();

        return collector()
                .check(() -> themeOnMain
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Mainpage.SKINS,
                                        morda.getLanguage()).replace("&nbsp;", " ")
                        )));
    }

    @Step("Disable theme on theme")
    default void disableThemeOnMain() {
        themeOnMain().should(displayed()).unCheck();
        saveButton().waitUntil(displayed()).click();
    }

    @Step("Do not open links in app")
    default void disableOpenLinksInApp() {
        openLiks().should(displayed()).unCheck();
        saveButton().waitUntil(displayed()).click();
    }

    @Step("Do not show mob version of services")
    default void disableMobVersion() {
        mobVersionSites().should(displayed()).unCheck();
        saveButton().waitUntil(displayed()).click();
    }

}
