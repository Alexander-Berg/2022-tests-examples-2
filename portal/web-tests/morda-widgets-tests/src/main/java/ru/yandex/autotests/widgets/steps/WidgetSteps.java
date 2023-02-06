package ru.yandex.autotests.widgets.steps;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.widgets.matchers.HasTextMatcher.hasText;
import static ru.yandex.autotests.widgets.matchers.StringContainsIgnoreCase.containsIgnoreCase;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23.07.13
 */
public class WidgetSteps {

    private CommonMordaSteps userSteps;
    private WidgetPage widgetPage;
    private WebDriver driver;

    public WidgetSteps(WebDriver driver) {
        this.driver = driver;
        this.widgetPage = new WidgetPage(driver);
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step
    public void shouldSeeWidgetLinks(List<HtmlElement> widgetLinks, Matcher<String> link) {
        for (HtmlElement element : widgetLinks) {
            userSteps.shouldSeeElementWithText(element, link);
        }
    }

    @Step
    public void shouldSeeWidgetWithTextIn(List<HtmlElement> elements, List<String> responses) {
        if (responses.size() == 0) {
            assertThat(elements, hasSize(0));
            return;
        }
        for (String response : responses) {
            assertThat(elements, Matchers.<HtmlElement>hasItem(hasText(containsIgnoreCase(response))));
        }
    }
}
