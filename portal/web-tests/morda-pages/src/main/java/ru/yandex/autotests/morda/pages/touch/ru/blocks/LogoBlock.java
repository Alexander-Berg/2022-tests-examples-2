package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Логотип")
@FindBy(xpath = "//div[contains(@class,'mlogo')]")
public class LogoBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Праздничный логотип")
    @FindBy(xpath = "//div[contains(@class, 'logo_custom_yes')]//img")
    private HtmlElement holidayLogotype;

    @Override
    @Step("Check logo")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        if (exists().matches(holidayLogotype)) {
            return collector()
                    .check(shouldSeeElement(holidayLogotype));
        }

        return collector()
                .check(shouldSeeElement(this));
    }
}
