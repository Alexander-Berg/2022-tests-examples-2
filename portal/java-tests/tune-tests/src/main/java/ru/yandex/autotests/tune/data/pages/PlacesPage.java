package ru.yandex.autotests.tune.data.pages;

import io.qameta.htmlelements.WebPage;
import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.HtmlElement;
import ru.yandex.autotests.morda.data.validation.Validateable;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.tune.data.element.Input;
import ru.yandex.autotests.tune.data.element.Logo;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;

import static io.qameta.htmlelements.matcher.DisplayedMatcher.displayed;
import static io.qameta.htmlelements.matcher.HasTextMatcher.hasText;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static ru.yandex.autotests.morda.data.TankerManager.getSafely;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.qatools.htmlelements.matchers.common.HasAttributeMatcher.hasAttribute;

/**
 * User: asamar
 * Date: 13.12.16
 */
public interface PlacesPage extends WebPage, Validateable<TuneMorda> {

    @FindBy("//h1")
    HtmlElement title();

    @FindBy("//div[contains(@class, 'geo-map_type_route')]")
    HtmlElement map();

    @FindBy("//li[1]/span[contains(@class, 'places-options__input')]")
    Input homeInput();

    @FindBy("//li[2]/span[contains(@class, 'places-options__input')]")
    Input workInput();

    @FindBy("//div[@class = 'places-options__desc']")
    HtmlElement descr();

    @FindBy("//div[@class = 'tune-footer__logo']")
    Logo logo();

    @Override
    @Step("Open places page")
    default void open(String baseUrl) {
        getWrappedDriver().get(fromUri(baseUrl).path("places").build().toString());
    }


    @Override
    @Step("Validate places page")
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(validateTitle(title(), validator))
                .check(validateDescr(descr(), validator))
                .check(validateHomeInput(homeInput(), validator))
                .check(validateWorkInput(workInput(), validator))
                .check(logo().validate(validator));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> title
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Tabs.PLACES, validator.getMorda().getLanguage())
                        ))
                );
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateDescr(HtmlElement descr, Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> descr
                        .should(displayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Places.DESC2, validator.getMorda().getLanguage())
                                        .replaceAll("&nbsp;", " ")
                                        .replaceAll("<br>", "\n")
                        ))
                );
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateHomeInput(Input homeInput,
                                                         Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> homeInput
                                .should(displayed())
//                        .should(hasText(
//                                getSafely(Dictionary.Tune.Region.HOME, validator.getMorda().getLanguage())
//                        ))
                )
                .check(() -> homeInput.input()
                        .should(hasAttribute("placeholder", getSafely(Dictionary.Tune.Region.HOME, validator.getMorda().getLanguage())))
                )
                .check(() -> homeInput.inputBox()
                        .should(displayed())
                )
                .check(() -> homeInput.inputGeo()
                        .should(displayed())
                );
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateWorkInput(Input workInput,
                                                         Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> workInput
                                .should(displayed())
//                        .should(hasText(
//                                getSafely(Dictionary.Tune.Region.WORK, validator.getMorda().getLanguage())
//                        ))
                )
                .check(() -> workInput.input()
                        .should(hasAttribute("placeholder", getSafely(Dictionary.Tune.Region.WORK, validator.getMorda().getLanguage())))
                )
                .check(() -> workInput.inputBox()
                        .should(displayed())
                )
                .check(() -> workInput.inputGeo()
                        .should(displayed())
                );
    }

}
