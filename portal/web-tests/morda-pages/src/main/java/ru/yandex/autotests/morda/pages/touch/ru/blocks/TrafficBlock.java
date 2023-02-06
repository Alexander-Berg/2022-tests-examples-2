package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.hamcrest.MatcherAssert;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: asamar
 * Date: 22.09.2015.
 */
@Name("Настроенный блок пробок")
@FindBy(xpath = "//div[contains(@class, 'informers3__long-item_type_traffic-personal')]")
public class TrafficBlock extends HtmlElement implements Validateable<TouchRuMorda> {


    @Name("Ссылка на настроенный блок пробок")
    @FindBy(xpath = ".//a[contains(@class, 'notifications_type_traffic__slide swiper__item')]")
    public HtmlElement directionLink;

    @Step("Check response status: \"{0}\"")
    public static HierarchicalErrorCollector validateDirectionLink(HtmlElement directionLink, Validator<? extends TouchRuMorda> validator) {
        if (exists().matches(directionLink)) {
            return collector()
                    .check(shouldSeeElement(directionLink))
                    .check(shouldHaveResponse(directionLink.getAttribute("href")));
        }
        return collector();
    }

    @Override
    @Step("Check direction link response status ")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(validateDirectionLink(directionLink, validator));
    }

    @Step("Check URL response status: \"{0}\" ")
    public static Runnable shouldHaveResponse(String url){
        Client client = MordaClient.getJsonEnabledClient();
        Response response = client.target(url)
                .request()
                .get();
        Response.Status status = Response.Status.fromStatusCode(response.getStatus());
        response.close();
        client.close();
        return () ->
            MatcherAssert.assertThat("Некорректная ссылка в настроенном блоке пробок", status, equalTo(Response.Status.OK));
    }

}
