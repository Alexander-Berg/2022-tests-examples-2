package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasAttribute;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("ТВ")
@FindBy(xpath = "//div[contains(@class, 'b-item-link__pos_main b-item-link__right')]")
public class TvBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h2")
    private HtmlElement header;

    @Name("Передачи")
    @FindBy(xpath = ".//div[@class='b-items__main_item']")
    private List<TvItem> items;

    public class TvItem extends HtmlElement {

        @Name("Программа")
        @FindBy(xpath = ".//p")
        private HtmlElement program;

        @Name("Канал")
        @FindBy(xpath = ".//small")
        private HtmlElement channel;
    }

    @Override
    @Step("Validate TV Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        shouldSeeElementMatchingTo(this,
                                hasAttribute("rel", equalTo("inner.html?tab=program")))
                )
                .check(
                        validateHeader(header, validator),
                        validateTvItems(items, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateHeader(HtmlElement header,
                                                             Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(header))
                .check(shouldSeeElementMatchingTo(header, hasText("Телепрограмма")));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTvItems(List<TvItem> items,
                                                             Validator<? extends DesktopHwLgV2Morda> validator) {
        HierarchicalErrorCollector collector = collector();

        items.forEach(item -> collector
                .check(shouldSeeElement(item))
                .check(
                        shouldSeeElement(item.program),
                        shouldSeeElement(item.channel)
                ));

        return collector;
    }
}
