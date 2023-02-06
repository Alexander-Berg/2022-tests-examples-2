package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
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
@FindBy(xpath = "//div[contains(@class, 'col_home-logo')]")
public class LogoBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

    @Name("Логотип")
    @FindBy(xpath = ".//div[contains(@class, 'home-logo__default')]")
    private HtmlElement logotype;

    @Name("Праздничный логотип")
    @FindBy(xpath = ".//img")
    private HtmlElement holidayLogotype;

    @Override
    @Step("Check logo")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        if (exists().matches(holidayLogotype)) {
            return collector()
                    .check(shouldSeeElement(holidayLogotype));
        }

        return collector()
                .check(shouldSeeElement(logotype));
    }
}
