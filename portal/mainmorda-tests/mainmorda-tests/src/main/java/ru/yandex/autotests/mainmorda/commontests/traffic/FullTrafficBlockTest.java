package ru.yandex.autotests.mainmorda.commontests.traffic;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TrafficData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TrafficSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.TRAFFIC;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.qatools.htmlelements.matchers.common.DoesElementExistMatcher.exists;

/**
 * User: eoff
 * Date: 18.02.13
 */
@Aqua.Test(title = "Полный блок пробок")
@Features({"Main", "Common", "Traffic Block"})
@Stories("Default View")
public class FullTrafficBlockTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TrafficSteps userTraffic = new TrafficSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userTraffic.ifFull();
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.trafficFullBlock);
    }

    @Test
    public void arrowTest() {
        user.shouldSeeElementMatchingTo(mainPage.trafficFullBlock.trafficArrow,
                TrafficData.ARROW_MATCHER);
    }

    @Test
    public void trafficDescriptionLink() {
        assumeThat(CONFIG.getBaseDomain(), not(equalTo(RU)));
        userTraffic.shouldSeeTrafficPoints();
        userLink.shouldSeeLink(mainPage.trafficFullBlock.trafficDescription, TrafficData.DESCRIPTION_LINK, TRAFFIC);
    }

    @Test
    public void trafficLink() {
        userLink.shouldSeeLink(mainPage.trafficFullBlock.trafficLink, TrafficData.TRAFFIC_LINK, TRAFFIC);
    }

    @Test
    public void trafficLights() {
        userLink.shouldSeeLink(mainPage.trafficFullBlock.trafficLights, TrafficData.LIGHTS_LINK, TRAFFIC);
    }

    @Test
    public void trafficForecastText() {
        assumeThat((CONFIG.domainIs(RU) || CONFIG.domainIs(UA)) && exists().matches(mainPage.trafficFullBlock.trafficForecast),
                is(true));
        user.shouldSeeElement(mainPage.trafficFullBlock.trafficForecast);
        user.shouldSeeElement(mainPage.trafficFullBlock.trafficForecast.forecastText);
        user.shouldSeeElementWithText(mainPage.trafficFullBlock.trafficForecast.forecastText,
                TrafficData.FORECAST_TEXT);
    }

    @Test
    public void trafficForecastItems() {
        assumeThat((CONFIG.domainIs(RU) || CONFIG.domainIs(UA)) && exists().matches(mainPage.trafficFullBlock.trafficForecast),
                is(true));
        user.shouldSeeElement(mainPage.trafficFullBlock.trafficForecast);
        userTraffic.shouldSeeCorrectForecastItems();
    }
}
