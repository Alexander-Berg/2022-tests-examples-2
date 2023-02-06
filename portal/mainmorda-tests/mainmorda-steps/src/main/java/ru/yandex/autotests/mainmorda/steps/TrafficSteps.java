package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.Matchers;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TrafficData;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.lessThan;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;

/**
 * User: eoff
 * Date: 18.02.13
 */
public class TrafficSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;

    public TrafficSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
    }

    @Step
    public void ifFull() {
        assumeFalse("In this domain we don't check traffic block", CONFIG.domainIs(KZ));
    }


    @Step
    public void switchToTrafficFrame() {
        driver.switchTo().frame(driver.findElement(By.xpath("//iframe[contains(@id,'wd-prefs-_traffic-')]")));
    }

    @Step
    public void switchToDefaultContent() {
        driver.switchTo().defaultContent();
    }

    @Step
    public void shouldSeeTrafficPoints() {
        String currentDescription = basePage.trafficFullBlock.trafficDescription.getText();
        if (!currentDescription.equals(TrafficData.DESCRIPTIONS.get(0))) {
            userSteps.shouldSeeElement(basePage.trafficFullBlock.trafficPoints);
            userSteps.shouldSeeElementWithText(basePage.trafficFullBlock.trafficPoints,
                    TrafficData.POINTS_MATCHER);
            String pointsText = basePage.trafficFullBlock.trafficPoints.getText();
            int points = Integer.parseInt(pointsText.substring(0, pointsText.indexOf(" ")));
            userSteps.shouldSeeElementWithText(basePage.trafficFullBlock.trafficPoints,
                    TrafficData.getPointsMatcher(points));
            userSteps.shouldSeeElementWithText(basePage.trafficFullBlock.trafficDescription,
                    equalTo(TrafficData.DESCRIPTIONS.get(points)));
        }
    }

    @Step
    public void shouldSeeCorrectForecastItems() {
        List<Integer> values =
                getIntegerValues(basePage.trafficFullBlock.trafficForecast.forecastValues);
        List<Integer> times =
                getIntegerValues(basePage.trafficFullBlock.trafficForecast.forecastTimes);

        assertThat(values, hasSize(times.size()));
        assertThat(values, everyItem(Matchers.greaterThanOrEqualTo(0)));
        assertThat(values, everyItem(Matchers.lessThanOrEqualTo(10)));
        if (times.size() > 0) {
            assertThat(basePage.trafficFullBlock.trafficForecast.forecastTimes.get(0).getText(),
                    TrafficData.FORECAST_HOUR_TEXT);
        }
        for (int i = 0; i != times.size() - 1; i++) {
            assertThat(times.get(i), anyOf(lessThan(times.get(i + 1)), equalTo(23)));
        }

    }

    private List<Integer> getIntegerValues(List<HtmlElement> elements) {
        List<Integer> intValues = new ArrayList<Integer>();
        for (HtmlElement element : elements) {
            intValues.add(Integer.parseInt(element.getText().split(" ")[0]));
        }
        return intValues;
    }
}
