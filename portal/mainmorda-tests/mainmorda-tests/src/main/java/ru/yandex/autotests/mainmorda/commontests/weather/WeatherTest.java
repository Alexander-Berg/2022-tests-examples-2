package ru.yandex.autotests.mainmorda.commontests.weather;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.WeatherData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.blocks.PageBlock.WEATHER;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * User: eoff
 * Date: 04.02.13
 */
@Aqua.Test(title = "Ссылки в виджете погоды")
@Features({"Main", "Common", "Weather Block"})
@Stories("Default View")
public class WeatherTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.weatherBlock);
    }

    @Test
    public void weatherLink() {
        userLink.shouldSeeLink(mainPage.weatherBlock.weatherBlockHeader.weatherLink, WeatherData.WEATHER, WEATHER);
    }

    @Test
    public void weatherIcon() {
        user.shouldSeeElement(mainPage.weatherBlock.weatherBlockHeader.weatherIcon);
        userLink.shouldSeeLink(mainPage.weatherBlock.weatherBlockHeader.weatherIconLink,
                WeatherData.WEATHER_ICON, WEATHER);
    }

    @Test
    public void weatherTemperature() {
        userLink.shouldSeeLink(mainPage.weatherBlock.weatherBlockHeader.currentTemperature,
                WeatherData.WEATHER_TEMP, WEATHER);
    }

    @Test
    public void forecastLinks() {
        user.shouldSeeElement(mainPage.weatherBlock.weatherForecast.forecastInfo);
        user.shouldSeeElementWithText(mainPage.weatherBlock.weatherForecast.forecastInfo,
                matches(WeatherData.FORECAST_PATTERN));
        userLink.shouldSeeLink(mainPage.weatherBlock.weatherForecast.forecastLink1,
                WeatherData.FORECAST_LINK1, WEATHER);
        userLink.shouldSeeLink(mainPage.weatherBlock.weatherForecast.forecastLink2,
                WeatherData.FORECAST_LINK2, WEATHER);
    }
}
