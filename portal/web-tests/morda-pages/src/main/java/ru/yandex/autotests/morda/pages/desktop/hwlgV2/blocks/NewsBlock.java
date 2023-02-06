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
@Name("Новости")
@FindBy(xpath = "//div[contains(@class, 'b-item-link__center')]")
public class NewsBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h2")
    private HtmlElement header;

    @Name("Новости")
    @FindBy(xpath = ".//ul/li")
    private List<HtmlElement> items;

    @Name("Котировки")
    @FindBy(xpath = ".//span[@class='b-quotes-item']")
    private List<HtmlElement> quotes;

    @Override
    @Step("Validate News Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        shouldSeeElementMatchingTo(this,
                                hasAttribute("rel", equalTo("inner.html?tab=news")))
                )
                .check(
                        validateHeader(header, validator),
                        validateNews(items, validator),
                        validateQuotes(quotes, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateHeader(HtmlElement header,
                                                            Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(header))
                .check(shouldSeeElementMatchingTo(header, hasText("Новости")));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateNews(List<HtmlElement> items,
                                                          Validator<? extends DesktopHwLgV2Morda> validator) {
        HierarchicalErrorCollector collector = collector();

        items.forEach(item -> collector
                .check(shouldSeeElement(item))
                .check(shouldSeeElementMatchingTo(item,
                        hasText(not(isEmptyOrNullString())))
                )
        );
        return collector;
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateQuotes(List<HtmlElement> items,
                                                            Validator<? extends DesktopHwLgV2Morda> validator) {
        HierarchicalErrorCollector collector = collector();

        items.forEach(item -> collector
                        .check(shouldSeeElement(item))
                        .check(shouldSeeElementMatchingTo(item,
                                        hasText(not(isEmptyOrNullString())))
                        )
        );
        return collector;
    }
}
