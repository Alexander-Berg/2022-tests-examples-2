package ru.yandex.autotests.morda.pages.desktop.com404.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;

/**
 * User: asamar
 * Date: 06.10.2015.
 */
@Name("Логотип")
@FindBy(xpath = "//a[contains(@class, 'logo_com')]")
public class LogoBlock extends HtmlElement implements Validateable<Com404Morda> {

    @Override
    @Step("Validate logo")
    public HierarchicalErrorCollector validate(Validator<? extends Com404Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(shouldSeeElementMatchingTo(this,
                        hasAttribute(HREF, equalTo("https://yandex.com/")))
                );
    }


}
