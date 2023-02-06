package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements;

import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.TabWithIcon;
import ru.yandex.autotests.morda.pages.touch.comtr.blocks.SearchBlock;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.morda.steps.CheckSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
public class SearchTab extends HtmlElement implements TabWithIcon {

    private static final CheckSteps CHECK_STEPS = new CheckSteps();

    @Name("Иконка информера")
    @FindBy(xpath = ".//div[contains(@class, 'informers__icon')]")
    private HtmlElement tabIcon;

    @Name("Текст информера")
    @FindBy(xpath = ".//div[contains(@class, 'informers__text')]")
    private HtmlElement tabText;

    @Name("Ссылка информера")
    @FindBy(xpath = ".")
    private HtmlElement tabLink;

    public HierarchicalErrorCollector checkTab(SearchTabs.SearchTabMatcher matcher) {
        return collector()
                .check(CHECK_STEPS.shouldSeeElement(this))
                .check(
                        validateTabIcon(matcher.getIconMatcher()),
                        validateTabText(matcher.getTextMatcher()),
                        validateTabLink(matcher.getHrefMatcher())
                );
    }

    @Step("Check informer icon")
    public HierarchicalErrorCollector validateTabIcon(Matcher<? super HtmlElement> iconMatcher) {
        return collector()
                .check(CHECK_STEPS.shouldSeeElement(tabIcon))
                .check(CHECK_STEPS.shouldSeeElementMatchingTo(tabIcon, iconMatcher));
    }

    @Step("Check informer text")
    public HierarchicalErrorCollector validateTabText(Matcher<? super HtmlElement> textMatcher) {
        return collector()
                .check(CHECK_STEPS.shouldSeeElement(tabText))
                .check(CHECK_STEPS.shouldSeeElementMatchingTo(tabText, textMatcher));
    }

    @Step("Check informer link")
    public HierarchicalErrorCollector validateTabLink(Matcher<? super HtmlElement> linkMatcher) {
        return collector()
                .check(CHECK_STEPS.shouldSeeElement(tabLink))
                .check(CHECK_STEPS.shouldSeeElementMatchingTo(tabLink, linkMatcher));
    }

    @Override
    public HtmlElement getTabIcon() {
        return tabIcon;
    }

    @Override
    public HtmlElement getTabText() {
        return tabText;
    }

    @Override
    public HtmlElement getTabLink() {
        return tabLink;
    }
}
