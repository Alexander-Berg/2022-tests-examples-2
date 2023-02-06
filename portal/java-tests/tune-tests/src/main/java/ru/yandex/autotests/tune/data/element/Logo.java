package ru.yandex.autotests.tune.data.element;

import io.qameta.htmlelements.annotation.FindBy;
import io.qameta.htmlelements.element.ExtendedWebElement;
import io.qameta.htmlelements.element.HtmlElement;
import ru.yandex.autotests.morda.data.validation.Validateable;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.qatools.allure.annotations.Step;

import static io.qameta.htmlelements.matcher.DisplayedMatcher.displayed;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: asamar
 * Date: 30.11.16
 */
public interface Logo extends ExtendedWebElement<Logo>, Validateable<TuneMorda>{

    @FindBy(".//a[contains(@class, 'logo')]")
    HtmlElement logo();

    @Step("Validate logo")
    @Override
    default HierarchicalErrorCollector validate(Validator<? extends TuneMorda> validator) {
        return collector()
                .check(() -> logo()
                        .should(displayed()));
    }



}
