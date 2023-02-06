package ru.yandex.autotests.widgets.steps;

import org.hamcrest.Matcher;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static junit.framework.Assert.fail;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.widgets.data.RegionsData.RegionCategories;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23.07.13
 */
public class RegionSteps {

    private CommonMordaSteps userSteps;
    private WidgetPage widgetPage;
    private WebDriver driver;

    public RegionSteps(WebDriver driver) {
        this.driver = driver;
        this.widgetPage = new WidgetPage(driver);
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step
    public void shouldSeeRegionalCategories(RegionCategories regionCategories) {
        for (String category : regionCategories.getRegions()) {
            shouldSeeCategory(widgetPage.regionalCategories, "?region=" + category);
        }
    }

    @Step
    public void shouldSeeCategory(List<HtmlElement> categories, String categoryName) {
        HtmlElement category = findCategory(categories, categoryName);
        if (category != null) {
            userSteps.shouldSeeElement(category);
        }
    }

    @Step
    public HtmlElement findCategory(List<HtmlElement> categories, String category) {
        for (HtmlElement element : categories) {
            if (hasAttribute(HREF, containsString(category)).matches(element)) {
                return element;
            }
        }
        fail("Категория " + category + " не найдена");
        return null;
    }

    @Step
    public void shouldSeeWidgetRegions(List<HtmlElement> links, Matcher<String> matcher) {
        for (HtmlElement link : links) {
            assertThat(link, hasAttribute(HREF, matcher));
        }
    }

}
