package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.lessThan;
import static javax.ws.rs.core.Response.Status.OK;
import static ru.yandex.autotests.mordamobile.data.TrafficData.FORECAST_HOUR_TEXT;
import static ru.yandex.autotests.mordamobile.data.TrafficData.getBallMatcher;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class TrafficSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public TrafficSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void shouldSeeForecastBalls() {
        for (HtmlElement element : homePage.trafficWidgetBlock.trafficForecast.forecasts) {
            assertThat(element, getBallMatcher(element));
        }
    }

    @Step
    public void shouldSeeForecastTimes() {
        List<Integer> times = new ArrayList<Integer>();

        for (HtmlElement element : homePage.trafficWidgetBlock.trafficForecast.forecastTimes) {
            times.add(Integer.parseInt(element.getText().split(" ")[0]));
        }

        forecastHourText(times);

        for (int i = 0; i != times.size() - 1; i++) {
            assertThat(times.get(i), anyOf(lessThan(times.get(i + 1)), equalTo(23)));
        }
    }

    private void forecastHourText(List<Integer> times) {
        if (times.size() > 0) {
            assertThat(homePage.trafficWidgetBlock.trafficForecast.forecastTimes.get(0).getText(),
                    FORECAST_HOUR_TEXT);
        }
    }

    @Step("Check URL response status")
    public void checkPersonalTrafficLink() {
        Client client = MordaClient.getJsonEnabledClient();
        Response response = client.target(homePage.trafficWidgetBlock.trafficLink.getAttribute("href"))
                .request()
                .get();
        Response.Status status = Response.Status.fromStatusCode(response.getStatus());
        response.close();
        client.close();
        assertThat("Некорректная ссылка в настроенном блоке пробок", status, equalTo(OK));
    }
}