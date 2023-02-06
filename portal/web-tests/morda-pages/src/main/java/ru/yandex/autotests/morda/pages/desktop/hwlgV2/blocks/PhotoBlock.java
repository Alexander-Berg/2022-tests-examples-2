package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.core.IsNot.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("Фото")
@FindBy(xpath = "//td[contains(@class, 'b-layout__col_right b-layout__col_bot b-layout__col_320')]")
public class PhotoBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Фон")
    @FindBy(xpath = ".//img")
    private HtmlElement background;

    @Name("Фото дня")
    @FindBy(xpath = ".//p")
    private HtmlElement text;

    @Name("Иконка")
    @FindBy(xpath = ".//i")
    private HtmlElement icon;


    @Override
    @Step("Validate Photo Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateBackground(background, validator),
                        validateText(text, validator),
                        validateIcon(icon, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateBackground(HtmlElement background,
                                                         Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(background))
                .check(shouldSeeElementMatchingTo(background,
                                hasAttribute(SRC, not(isEmptyOrNullString())))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateText(HtmlElement text,
                                                           Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(text))
                .check(shouldSeeElementMatchingTo(text,
                                hasText("Фото дня"))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateIcon(HtmlElement icon,
                                                              Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(icon));
    }
}
