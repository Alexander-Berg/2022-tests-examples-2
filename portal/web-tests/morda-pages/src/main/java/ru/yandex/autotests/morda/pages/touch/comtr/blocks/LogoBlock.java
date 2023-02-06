package ru.yandex.autotests.morda.pages.touch.comtr.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Логотип")
@FindBy(xpath = "//div[contains(@class,'mlogo__container')]//div[contains(@class,'mlogo')]")
public class LogoBlock extends HtmlElement implements Validateable<TouchComTrMorda> {

    @Name("Праздничный логотип")
    @FindBy(xpath = "//div[contains(@class, 'mlogo_custom_yes')]//img")
    private HtmlElement holidayLogotype;

    @Override
    @Step("Check logo")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        if (exists().matches(holidayLogotype)) {
            return collector()
                    .check(shouldSeeElement(holidayLogotype));
        }

        return collector()
                .check(shouldSeeElement(this))
                .check(shouldSeeElementMatchingTo(this, hasAttribute(CLASS, containsString("mlogo"))));
    }
}
