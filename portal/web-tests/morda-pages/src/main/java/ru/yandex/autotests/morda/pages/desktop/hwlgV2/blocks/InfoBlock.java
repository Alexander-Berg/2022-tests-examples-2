package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

import org.hamcrest.CoreMatchers;
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
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasAttribute;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("Инфо")
@FindBy(xpath = "//td[contains(@class, 'b-hint__3col_item_2')]/div")
public class InfoBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("INFO")
    @FindBy(xpath = ".//i")
    private HtmlElement info;

    @Name("Изменить город")
    @FindBy(xpath = ".//h3")
    private HtmlElement text;

    @Override
    @Step("Validate Info Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        shouldSeeElementMatchingTo(this,
                                hasAttribute("rel", CoreMatchers.equalTo("cityselect.html?page=index.html")))
                )
                .check(
                        validateInfo(info, validator),
                        validateText(text, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateInfo(HtmlElement info,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(info));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateText(HtmlElement text,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(text))
                .check(shouldSeeElementMatchingTo(text, hasText(equalTo("Изменить город"))));
    }


}
