package ru.yandex.autotests.mordamobile.traffic;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.steps.TrafficSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordamobile.data.TrafficData.FORECAST_TITLE;
import static ru.yandex.autotests.mordamobile.data.TrafficData.POINTS_MATCHER;
import static ru.yandex.autotests.mordamobile.data.TrafficData.TITLE;
import static ru.yandex.autotests.mordamobile.data.TrafficData.TRAFFIC_LINK;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок пробок")
@Features("Traffic")
public class TrafficTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private TrafficSteps userTraffic = new TrafficSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(),CONFIG.getBaseDomain().getCapital() , CONFIG.getLang());
        user.shouldSeeElement(homePage.trafficWidgetBlock);
    }

    @Test
    public void trafficTitle() {
        user.shouldSeeElement(homePage.trafficWidgetBlock.title);
        user.shouldSeeElementWithText(homePage.trafficWidgetBlock.title, TITLE);
    }

    @Test
    public void trafficIcon() {
        user.shouldSeeElement(homePage.trafficWidgetBlock.icon);
    }

    @Test
    public void trafficLink() {
        user.shouldSeeLinkLight(homePage.trafficWidgetBlock.trafficLink, TRAFFIC_LINK);
    }

    @Test
    public void trafficNum() {
        assumeThat(homePage.trafficWidgetBlock.trafficNum, exists());
        user.shouldSeeElement(homePage.trafficWidgetBlock.trafficNum);
        user.shouldSeeElementWithText(homePage.trafficWidgetBlock.trafficNum,
                POINTS_MATCHER);
    }

    @Test
    public void trafficForecastTitle() {
        assumeThat(homePage.trafficWidgetBlock.trafficForecast, exists());
        user.shouldSeeElement(homePage.trafficWidgetBlock.trafficForecast.title);
        user.shouldSeeElementWithText(homePage.trafficWidgetBlock.trafficForecast.title, FORECAST_TITLE);
    }

    @Test
    public void trafficForecastBalls() {
        assumeThat(homePage.trafficWidgetBlock.trafficForecast, exists());
        userTraffic.shouldSeeForecastBalls();
    }

    @Test
    public void trafficForecasts() {
        assumeThat(homePage.trafficWidgetBlock.trafficForecast, exists());
        user.shouldSeeListWithSize(homePage.trafficWidgetBlock.trafficForecast.forecastTimes,
                equalTo(homePage.trafficWidgetBlock.trafficForecast.forecastTimes.size()));
    }

    @Test
    public void trafficForecastTimes() {
        assumeThat(homePage.trafficWidgetBlock.trafficForecast, exists());
        userTraffic.shouldSeeForecastTimes();
    }

    @Test
    public void trafficPersonalBlockLink() throws InterruptedException {
        driver.manage().addCookie(
                new Cookie(
                        "wp",
                        "1..c8ztYQ..1445959833788749..._WfOvqg.75081079.1406.5d0af6a031362fc0526a7eb53fc93467",
                        ".yandex.ru",
                        null,
                        null));
        driver.navigate().refresh();
        user.shouldSeeElement(homePage.trafficWidgetBlock);
        user.shouldSeeElement(homePage.trafficWidgetBlock.trafficPersonal);
        userTraffic.checkPersonalTrafficLink();
    }
}
