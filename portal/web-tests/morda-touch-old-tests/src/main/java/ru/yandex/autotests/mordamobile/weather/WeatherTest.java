package ru.yandex.autotests.mordamobile.weather;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.mordamobile.data.WeatherData.FORECAST;
import static ru.yandex.autotests.mordamobile.data.WeatherData.TITLE;
import static ru.yandex.autotests.mordamobile.data.WeatherData.WEATHER_LINK;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Информер погоды")
@Features("Weather")
public class WeatherTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.weatherBlock);
    }

    @Test
    public void weatherTitle() {
        user.shouldSeeElement(homePage.weatherBlock.title);
        user.shouldSeeElementWithText(homePage.weatherBlock.title, TITLE);
    }

    @Test
    public void forecast() {
        user.shouldSeeElement(homePage.weatherBlock.forecast);
        user.shouldSeeElementWithText(homePage.weatherBlock.forecast,
                FORECAST);
    }

    @Test
    public void weatherIcon() {
        user.shouldSeeElement(homePage.weatherBlock.icon);
    }

    @Test
    public void weatherLink() {
        user.shouldSeeLink(homePage.weatherBlock.weatherLink, WEATHER_LINK);
    }
}
