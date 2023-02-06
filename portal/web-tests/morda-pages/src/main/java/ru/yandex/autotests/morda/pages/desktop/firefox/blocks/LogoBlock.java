package ru.yandex.autotests.morda.pages.desktop.firefox.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Логотип")
@FindBy(xpath = "//td[contains(@class, 'main__item__logo')]//div[contains(@class, 'logo')]")
public class LogoBlock extends HtmlElement implements Validateable<DesktopFirefoxMorda> {

    @Name("Ссылка логотипа")
    @FindBy(xpath = ".//a[contains(@class, 'logo__link')]")
    private HtmlElement logotypeLink;

    @Override
    @Step("Check logo")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(shouldSeeElement(logotypeLink))
                .check(
                        shouldSeeElementMatchingTo(logotypeLink, hasAttribute(HREF, startsWith(validator.getCleanvars().getWWW())))
                );
    }
}
