package ru.yandex.autotests.tune.data.pages;

import io.qameta.htmlelements.WebPage;
import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.ExtendedList;
import io.qameta.htmlelements.element.HtmlElement;
import ru.yandex.autotests.morda.data.validation.Validateable;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.tune.data.element.LangItem;
import ru.yandex.autotests.tune.data.element.Logo;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static io.qameta.htmlelements.matcher.DisplayedMatcher.displayed;
import static io.qameta.htmlelements.matcher.HasTextMatcher.hasText;
import static java.lang.Thread.sleep;
import static java.util.stream.Collectors.toList;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.collection.IsCollectionWithSize.hasSize;
import static ru.yandex.autotests.morda.data.TankerManager.getSafely;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.qatools.htmlelements.matchers.common.IsElementDisplayedMatcher.isDisplayed;

/**
 * User: asamar
 * Date: 24.11.16
 */
public interface LangPage extends WebPage, Validateable<TuneMorda> {

    @FindBy("//label[@class = 'touch-select__l']")
    ExtendedList<LangItem> languages();

    @FindBy("//button[contains(@class, 'form__save')]")
    HtmlElement saveButton();

    @FindBy("//div[@class = 'tune-footer__logo']")
    Logo logo();

    @FindBy("//h1[@class = 'tune-header__title']")
    HtmlElement header();

    @FindBy("//a[contains(@class, 'tune-header__back')]")
    HtmlElement headerBack();

    @Step("Select lang by number {0}")
    default void selectLang(int num) {
        languages().waitUntil(hasSize(greaterThan(0))).should("Языки не отображаются", hasSize(greaterThan(0)))
                .get(num)
                .should("Язык " + num + "отсутствует ", isDisplayed())
                .click();
        saveButton().should("Не получилось сохранить", isDisplayed()).click();
    }

    @Step("Select lang following by {0}")
    default String selectNextLang(MordaLanguage currentLang) throws InterruptedException {
        List<String> values = languages().stream()
                .map(LangItem::getValue)
                .collect(toList());

        int currentIndex = values.indexOf(currentLang.getValue());

        if (currentIndex >= 0) {
            int targetIndex = (currentIndex + 1) % languages().size();
            languages().get(targetIndex).should(displayed()).click();
            saveButton().should(displayed()).click();
            sleep(1000);
            refresh();
            return values.get(targetIndex);
        }
        throw new RuntimeException("Some shit happened");
    }

    @Step("Refresh")
    default void refresh() {
        getWrappedDriver().navigate().refresh();
    }

    @Override
    @Step("Open lang page")
    default void open(String baseUrl) {
        getWrappedDriver().get(fromUri(baseUrl).path("lang").build().toString());
    }

    @Override
    @Step("Validate lang page")
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(logo().validate(validator))
                .check(validateHeader(header(), validator))
//                .check(validateReturnBack(headerBack(), validator))
                .check(validateLanguages(validator));
    }

    @Step("Validate languages")
    default HierarchicalErrorCollector validateLanguages(Validator<? extends TuneMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != languages().size(); i++) {
            collector.check(validateLanguage(languages().get(i), validator));
        }

        collector.check(() -> languages().should(hasSize(6)));

        return collector;

    }

    @Step("{0}")
    default HierarchicalErrorCollector validateLanguage(LangItem language, Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> language
                        .should(isDisplayed())
                        .should(hasText(
                                getSafely("tune","lang", language.getValue() , validator.getMorda().getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateHeader(HtmlElement header, Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> header
                        .should(isDisplayed())
                        .should(hasText(
                                getSafely(Dictionary.Tune.Tabs.LANG, validator.getMorda().getLanguage())
                        )));
    }

    @Step("{0}")
    default HierarchicalErrorCollector validateReturnBack(HtmlElement returtBack,
                                                          Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> returtBack.should(isDisplayed()));
    }

}
