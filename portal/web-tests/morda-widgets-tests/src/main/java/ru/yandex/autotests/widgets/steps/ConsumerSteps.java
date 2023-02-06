package ru.yandex.autotests.widgets.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.widgets.data.ConsumerData.CONSUMER_LINK;
import static ru.yandex.autotests.widgets.data.ConsumerData.CONSUMER_URL;
import static ru.yandex.autotests.widgets.pages.WidgetPage.CategoryElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.07.13
 */
public class ConsumerSteps {

    public static final int NEXT_PAGE_CLICKS = 10;


    private CommonMordaSteps userSteps;
    private WidgetPage widgetPage;
    private WebDriver driver;

    public ConsumerSteps(WebDriver driver) {
        this.driver = driver;
        this.widgetPage = new WidgetPage(driver);
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step
    public void shouldSeeConsumerInLinks(List<? extends HtmlElement> links) {
        for (int i = 0; i != links.size(); i++) {
            userSteps.shouldSeeLink(links.get(i), CONSUMER_LINK);
            userSteps.opensPage(CONSUMER_URL);
        }
    }

    @Step
    public void shouldSeeConsumerInCategories(List<CategoryElement> categories) {
        for (int i = 1; i != categories.size(); i++) {
            userSteps.shouldSeeLink(categories.get(i).link, CONSUMER_LINK);
            userSteps.opensPage(CONSUMER_URL);
        }
    }

    @Step
    public void shouldSeeConsumerInPager() {
        for (int i = 0; i != NEXT_PAGE_CLICKS; i++) {
            userSteps.shouldSeeElement(widgetPage.nextPageButton);
            userSteps.shouldSeeElementMatchingTo(widgetPage.nextPageButton,
                    hasAttribute(HREF, CONSUMER_LINK.url));
            userSteps.shouldSeePage(CONSUMER_LINK.url);
            userSteps.clicksOn(widgetPage.nextPageButton);
        }
    }
}
