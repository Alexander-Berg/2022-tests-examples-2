package ru.yandex.autotests.hwmorda.bmw;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.hwmorda.Properties;
import ru.yandex.autotests.hwmorda.pages.BmwPage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.hwmorda.data.BMWRubricData.TOPNEWS_URL;
import static ru.yandex.autotests.hwmorda.data.BMWRubricData.TUNE_URL;
import static ru.yandex.autotests.hwmorda.data.BMWRubricData.WEATHER_URL;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: alex89
 * Date: 17.09.12
 */

@Aqua.Test(title = "BMW - проверка наличия блоков на главной странице и переходов по ссылкам")
@Features("Bmw")
@Stories("Actions")
public class BmwMainPageTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private BmwPage bmwPage = new BmwPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBMWBaseUrl());
//        user.setsRegion(MOSCOW, CONFIG.getBMWBaseUrl());
    }

    @Test
    public void logotypeOnBmwMainPage() {
        user.shouldSeeElement(bmwPage.logo);
        user.clicksOn(bmwPage.logo);
        user.shouldSeePage(CONFIG.getBMWBaseUrl());
    }

    @Test
    public void trafficRubricCanBeSwitchedOnBmwMainPage() {
        user.shouldSeeElement(bmwPage.trafficButton);
        user.clicksOn(bmwPage.trafficButton);
        user.shouldSeeElementIsSelected(bmwPage.trafficButton);
        user.shouldSeeElement(bmwPage.trafficWidget);
        user.shouldSeePage(CONFIG.getBMWBaseUrl());
    }

    @Test
    public void weatherRubricSwitchingOnBmwMainPage() {
        user.shouldSeeElement(bmwPage.weatherButton);
        user.clicksOn(bmwPage.weatherButton);
        user.shouldSeeElementIsSelected(bmwPage.weatherButton);
        user.shouldSeeElement(bmwPage.weatherWidget);
        user.shouldSeePage(WEATHER_URL);
    }

    @Test
    public void newsRubricSwitchingOnBmwMainPage() {
        user.shouldSeeElement(bmwPage.newsButton);
        user.clicksOn(bmwPage.newsButton);
        user.shouldSeeElementIsSelected(bmwPage.newsButton);
        user.shouldSeeElement(bmwPage.newsWidget);
        user.shouldSeePage(TOPNEWS_URL);
    }

    @Test
    public void stocksRubricOnBmwMainPage() {
        user.shouldSeeElement(bmwPage.stocksArea);
        user.clicksOn(bmwPage.stocksArea);
        user.shouldSeePage(CONFIG.getBMWBaseUrl());
    }

    @Test
    public void crossRubricSwitchingOnBmwMainPage() {
        user.clicksOn(bmwPage.newsButton);
        user.shouldSeeElement(bmwPage.newsWidget);
        user.clicksOn(bmwPage.weatherButton);
        user.shouldSeeElement(bmwPage.weatherWidget);
        user.clicksOn(bmwPage.trafficButton);
        user.shouldSeeElement(bmwPage.trafficWidget);
    }

    @Test
    public void changeRegionActionOnBmwMainPage() {
        user.shouldSeeElement(bmwPage.regionName);
        user.clicksOn(bmwPage.regionName);
        user.shouldSeeElement(bmwPage.changeRegionWidget);
        user.shouldSeePage(TUNE_URL);
    }
}
