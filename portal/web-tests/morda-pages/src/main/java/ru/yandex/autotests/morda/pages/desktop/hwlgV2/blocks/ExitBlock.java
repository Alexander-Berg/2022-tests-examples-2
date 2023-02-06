package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda;
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
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("Выйти из LG Smart TV")
@FindBy(xpath = "//div[contains(@class, 'b-item-link__exit')]")
public class ExitBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Иконка")
    @FindBy(xpath = ".//i")
    private HtmlElement icon;

    @Name("Выйти из LG Smart TV")
    @FindBy(xpath = ".//h3")
    private HtmlElement text;

    @Override
    @Step("Validate Exit Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateIcon(icon, validator),
                        validateText(text, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateIcon(HtmlElement icon,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(icon));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateText(HtmlElement text,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(text))
                .check(shouldSeeElementMatchingTo(text, hasText(equalTo("Выйти из LG Smart TV"))));
    }
}
