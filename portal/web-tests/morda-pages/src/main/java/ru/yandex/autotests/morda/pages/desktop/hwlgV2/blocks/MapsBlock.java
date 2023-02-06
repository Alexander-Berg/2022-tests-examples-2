package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasAttribute;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("Карта")
@FindBy(xpath = "//td[contains(@class, 'b-layout__col_left b-layout__col_top b-layout__col_320')]/div[2]")
public class MapsBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Иконка")
    @FindBy(xpath = ".//i")
    private HtmlElement icon;

    @Name("Баллы")
    @FindBy(xpath = ".//h1")
    private HtmlElement text;

    @Name("Описание пробок")
    @FindBy(xpath = ".//p")
    private HtmlElement description;

    @Override
    @Step("Validate Maps Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        shouldSeeElementMatchingTo(this,
                                hasAttribute("rel", equalTo("inner.html?tab=red")))
                )
                .check(
                        validateIcon(icon, validator),
                        validateText(text, validator),
                        validateDescription(description, validator)
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
                .check(shouldSeeElementMatchingTo(text, hasText(not(isEmptyOrNullString()))));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateDescription(HtmlElement description,
                                                                 Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(description))
                .check(shouldSeeElementMatchingTo(description, hasText(not(isEmptyOrNullString()))));
    }
}
