package ru.yandex.autotests.morda.pages.desktop.comtrall.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.comtrall.DesktopComTrAllMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Логотип")
@FindBy(xpath = "//div[@class='logo']/div")
public class LogoBlock extends HtmlElement implements Validateable<DesktopComTrAllMorda> {

    @Override
    @Step("Check logo")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComTrAllMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(shouldSeeElementMatchingTo(this, allOfDetailed(
                        hasAttribute(CLASS, containsString("logo__type_en")),
                        hasAttribute(CLASS, containsString("logo__image_bg"))
                )));

    }
}
