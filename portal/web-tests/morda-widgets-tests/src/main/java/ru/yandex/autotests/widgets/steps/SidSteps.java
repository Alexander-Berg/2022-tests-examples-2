package ru.yandex.autotests.widgets.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.widgets.data.SidData.SID_MATCHER;

/**
 * User: ivannik
 * Date: 01.08.13
 * Time: 19:02
 */
public class SidSteps {

    private CommonMordaSteps userSteps;
    private WidgetPage widgetPage;
    private WebDriver driver;

    public SidSteps(WebDriver driver) {
        this.driver = driver;
        this.widgetPage = new WidgetPage(driver);
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step
    public void shouldSeeSidInUrl(List<String> urls) {
        assertThat("Не найден sid в ссылках: " + urls.toString(), urls, hasItem(SID_MATCHER));
    }

    private <E extends HtmlElement> E getRandomElementFrom(List<E> elements) {
        List<E> el = new ArrayList<E>(elements);
        Collections.shuffle(el);
        return el.get(0);
    }

    @Step
    public <E extends HtmlElement> void clicksOnRandomElementIn(List<E> elements) {
        userSteps.clicksOn(getRandomElementFrom(elements));
    }
}
