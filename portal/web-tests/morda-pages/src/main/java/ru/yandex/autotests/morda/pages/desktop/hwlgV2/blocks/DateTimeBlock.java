package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("Дата/время, регион")
@FindBy(xpath = "//div[@class='b-city-info__main']")
public class DateTimeBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Время")
    @FindBy(xpath = ".//h1")
    private HtmlElement time;

    @Name("Время")
    @FindBy(xpath = ".//p[1]")
    private HtmlElement date;

    @Name("Время")
    @FindBy(xpath = ".//p[2]")
    private HtmlElement region;

    @Override
    @Step("Validate DateTime Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTime(time, validator),
                        validateDate(date, validator),
                        validateRegion(region, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTime(HtmlElement time,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(time));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateDate(HtmlElement date,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(date));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateRegion(HtmlElement region,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(region));
    }
}
