package ru.yandex.autotests.morda.pages.desktop.yaru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda;
import ru.yandex.autotests.morda.pages.desktop.yaru.htmlelements.HeaderAuthorized;
import ru.yandex.autotests.morda.pages.desktop.yaru.htmlelements.HeaderUnauthorized;
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
@Name("Хедер")
@FindBy(xpath = "//tr[contains(@class, 'layout__header')]")
public class HeaderBlock extends HtmlElement implements Validateable<DesktopYaruMorda> {

    private HeaderAuthorized headerAuthorized;
    private HeaderUnauthorized headerUnauthorized;

    @Override
    @Step("Check header")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopYaruMorda> validator) {
        HierarchicalErrorCollector collector = collector()
                .check(shouldSeeElement(this));
        if (validator.getUser() != null) {
            return collector
                    .check(headerAuthorized.validate(validator));
        } else {
            return collector
                    .check(headerUnauthorized.validate(validator));
        }
    }
}
