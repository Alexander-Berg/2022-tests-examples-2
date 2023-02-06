package ru.yandex.autotests.morda.pages.desktop.page404.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Логотип")
@FindBy(xpath = "//div[contains(@class, 'layout__line_top')]//a[contains(@class, 'logo')]")
public class LogoBlock extends HtmlElement implements Validateable<Desktop404Morda> {

    @Override
    @Step("Check logo")
    public HierarchicalErrorCollector validate(Validator<? extends Desktop404Morda> validator) {
        return collector()
                .check(shouldSeeElement(this));
    }
}
