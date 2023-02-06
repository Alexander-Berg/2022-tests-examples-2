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
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasAttribute;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("Афиша")
@FindBy(xpath = "//div[contains(@class, 'b-item-link__pos_main b-item-link__left')]")
public class AfishaBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h2")
    private HtmlElement header;

    @Name("Список фильмов")
    @FindBy(xpath = ".//div[@class='b-items__main_item']")
    private List<AfishaItem> items;

    public static class AfishaItem extends HtmlElement {

        @Name("Заголовок")
        @FindBy(xpath = ".//p")
        private HtmlElement title;

        @Name("Жанр")
        @FindBy(xpath = ".//small")
        private HtmlElement description;
    }

    @Override
    @Step("Validate Afisha Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        shouldSeeElementMatchingTo(this,
                                hasAttribute("rel", equalTo("inner.html?tab=afisha")))
                )
                .check(
                        validateHeader(header, validator),
                        validateAfishaItems(items, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateHeader(HtmlElement title,
                                                            Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(shouldSeeElementMatchingTo(title, hasText("Афиша")));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateAfishaItems(List<AfishaItem> items,
                                                                 Validator<? extends DesktopHwLgV2Morda> validator) {
        HierarchicalErrorCollector collector = collector().check(
                shouldSeeElementMatchingTo(items, hasSize(4)));

        items.forEach(item -> collector
                        .check(shouldSeeElement(item))
                        .check(shouldSeeElementMatchingTo(item.title,
                                        hasText(not(isEmptyOrNullString()))
                                ),
                                shouldSeeElementMatchingTo(item.description,
                                        hasText(not(isEmptyOrNullString()))
                                )
                        )
        );

        return collector;
    }


}
