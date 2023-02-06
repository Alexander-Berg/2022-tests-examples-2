package ru.yandex.autotests.tune.data.pages;

import io.qameta.htmlelements.WebPage;
import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.HtmlElement;
import ru.yandex.autotests.morda.data.validation.Validateable;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.tune.data.element.Logo;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;

import static io.qameta.htmlelements.matcher.DisplayedMatcher.displayed;
import static io.qameta.htmlelements.matcher.HasTextMatcher.hasText;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.CoreMatchers.startsWith;
import static ru.yandex.autotests.morda.data.TankerManager.getSafely;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.qatools.htmlelements.matchers.common.HasAttributeMatcher.hasAttribute;

/**
 * User: asamar
 * Date: 05.12.16
 */
public interface MainPage extends WebPage, Validateable<TuneMorda> {

    @FindBy("//h1")
    HtmlElement title();

    @FindBy("//div[@class = 'tune-footer__logo']")
    Logo logo();

    @FindBy("//div[@class = 'tune-footer__links']")
    Footer footer();

    @FindBy("//ul[contains(@class, 'index-options')]")
    Settings settings();


    @Override
    @Step("Open main page")
    default void open(String baseUrl) {
        getWrappedDriver().get(baseUrl);
    }


    @Override
    @Step("Validate main page")
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(settings().validate(validator))
                .check(footer().validate(validator))
                .check(logo().validate(validator))
                .check(validateTitle(title(), validator));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> title
                        .should(displayed())
                        .should(hasText(getSafely(Dictionary.Tune.Tabs.INDEX, validator.getMorda().getLanguage()))));
    }

    interface Footer extends HtmlElement, Validateable<TuneMorda> {

        @FindBy(".//a[1]")
        HtmlElement feedback();

        @FindBy(".//a[2]")
        HtmlElement fullVersion();

        @Override
        @Step("Validate footer")
        default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
            return collector()
                    .check(validateFeedback(feedback(), validator))
                    .check(validateFullVersion(fullVersion(), validator));
        }

        @Step("{0}")
        default HierarchicalErrorCollector validateFeedback(HtmlElement feedback,
                                                            Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> feedback
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Common.FEEDBACK, morda.getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(
                                    fromUri(morda.getBaseUrl())
                                            .path("support")
                                            .toString()))
                            ));
        }

        @Step("{0}")
        default HierarchicalErrorCollector validateFullVersion(HtmlElement fullVersion,
                                                               Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> fullVersion
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Common.FOOT_FULL, morda.getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(
                                    fromUri(morda.getBaseUrl())
                                            .path("/portal/set/any/")
                                            .build()
                                            .toString())
                            )));
        }


    }

    interface Settings extends HtmlElement, Validateable<TuneMorda> {

        @FindBy("//a[@data-statlog = 'tabs.geo']")
        HtmlElement geo();

        @FindBy("//a[@data-statlog = 'tabs.places']")
        HtmlElement places();

        @FindBy("//a[@data-statlog = 'tabs.lang']")
        HtmlElement lang();

        @FindBy("//a[@data-statlog = 'tabs.search']")
        HtmlElement search();

        @FindBy("//a[@data-statlog = 'tabs.common']")
        HtmlElement common();

        @FindBy("//a[@data-statlog = 'tabs.adv']")
        HtmlElement adv();


        @Override
        @Step("Validate settings")
        default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
            MordaType mordaType = validator.getMorda().getMordaType();

            switch (mordaType) {
                case TOUCH_TUNE: return validateMain(validator);
                case TOUCH_COMTR_TUNE: return validateComTr(validator);
                case TOUCH_COM_TUNE: return validateCom(validator);
                default: return collector();
            }
        }

        @Step("Validate settings")
        default HierarchicalErrorCollector validateMain(Validator<? extends TuneMorda> validator) {
            return collector()
                    .check(validateGeo(geo(), validator))
                    .check(validatePlaces(places(), validator))
                    .check(validateLang(lang(), validator))
                    .check(validateSearch(search(), validator))
                    .check(validateCommon(common(), validator))
                    .check(validateAdv(adv(), validator));
        }

        @Step("Validate settings")
        default HierarchicalErrorCollector validateCom(Validator<? extends TuneMorda> validator) {
            return collector()
                    .check(validateGeo(geo(), validator))
                    .check(validateSearch(search(), validator))
                    .check(validateCommon(common(), validator))
                    .check(validateAdv(adv(), validator));
        }

        @Step("Validate settings")
        default HierarchicalErrorCollector validateComTr(Validator<? extends TuneMorda> validator) {
            return collector()
                    .check(validateGeo(geo(), validator))
                    .check(validatePlaces(places(), validator))
                    .check(validateSearch(search(), validator))
                    .check(validateCommon(common(), validator));
        }


        @Step("{0}")
        default HierarchicalErrorCollector validateGeo(HtmlElement geo,
                                                       Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> geo
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Tabs.GEO, morda.getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(morda.getUrl() + "geo"))));
        }

        @Step("{0}")
        default HierarchicalErrorCollector validatePlaces(HtmlElement places,
                                                          Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> places
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Tabs.PLACES, morda.getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(morda.getUrl() + "places"))));
        }

        @Step("{0}")
        default HierarchicalErrorCollector validateLang(HtmlElement lang,
                                                        Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> lang
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Tabs.LANG, morda.getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(morda.getUrl() + "lang"))));
        }

        @Step("{0}")
        default HierarchicalErrorCollector validateSearch(HtmlElement search,
                                                          Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> search
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Tabs.SEARCH, morda.getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(morda.getUrl() + "search"))));
        }

        @Step("{0}")
        default HierarchicalErrorCollector validateCommon(HtmlElement common,
                                                          Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> common
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Tabs.COMMON, validator.getMorda().getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(validator.getMorda().getUrl() + "common"))));
        }

        @Step("{0}")
        default HierarchicalErrorCollector validateAdv(HtmlElement adv,
                                                       Validator<? extends TuneMorda> validator) {
            TuneMorda morda = validator.getMorda();

            return collector()
                    .check(() -> adv
                            .should(displayed())
                            .should(hasText(
                                    getSafely(Dictionary.Tune.Tabs.ADV, morda.getLanguage())
                            ))
                            .should(hasAttribute("href", startsWith(morda.getUrl() + "adv"))));
        }


    }

}
