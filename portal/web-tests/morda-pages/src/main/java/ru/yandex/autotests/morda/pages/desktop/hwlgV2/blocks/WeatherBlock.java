package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

/**
 * User: asamar
 * Date: 30.10.2015.
 */

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers;

import static org.hamcrest.CoreMatchers.anyOf;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.startsWith;
import static org.hamcrest.core.IsNot.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

@Name("Погода")
@FindBy(xpath = "//div[contains(@class, 'b-colorblock__type_green')]")
public class WeatherBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Погода сейчас")
    @FindBy(xpath = ".//h1")
    private HtmlElement now;

    @Name("Погода ночью")
    @FindBy(xpath = ".//p[1]")
    private HtmlElement night;

    @Name("Погода завтра")
    @FindBy(xpath = ".//p[2]")
    private HtmlElement tomorrow;

    @Name("Иконка")
    @FindBy(xpath = ".//img")
    private HtmlElement icon;

    @Override
    @Step("Validate Weather Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        shouldSeeElementMatchingTo(this,
                                WrapsElementMatchers.hasAttribute("rel", equalTo("inner.html?tab=green")))
                )
                .check(
                        validateNow(now, validator),
                        validateNight(night, validator),
                        validateTomorrow(tomorrow, validator),
                        validateIcon(icon, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateNow(HtmlElement now,
                                                         Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(now))
                .check(shouldSeeElementMatchingTo(now,
                                hasText(not(isEmptyOrNullString())))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateNight(HtmlElement night,
                                                           Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(night))
                .check(shouldSeeElementMatchingTo(night,
                                hasText(not(isEmptyOrNullString())))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTomorrow(HtmlElement tomorrow,
                                                              Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(tomorrow))
                .check(shouldSeeElementMatchingTo(tomorrow,
                                hasText(not(isEmptyOrNullString())))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateIcon(HtmlElement img,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {

        String scheme = validator.getMorda().getScheme();
        return collector()
                .check(shouldSeeElement(img))
                .check(shouldSeeElementMatchingTo(img,
                                hasAttribute(SRC, anyOf(
                                                startsWith("http://yandex.st/weather/i/icons"),
                                                startsWith(scheme + "://yastatic.net/weather/i/icons"))
                                )
                        )
                );
    }
}
