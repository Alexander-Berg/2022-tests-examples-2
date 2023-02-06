package ru.yandex.autotests.hwmorda.lg;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.hwmorda.Properties;
import ru.yandex.autotests.hwmorda.pages.LgMainPage;
import ru.yandex.autotests.hwmorda.pages.LgSubPage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.hwmorda.data.LgRubricData.FOTKI_URL;
import static ru.yandex.autotests.hwmorda.data.LgRubricData.STOCKS_URL;
import static ru.yandex.autotests.hwmorda.data.LgRubricData.TOPNEWS_URL;
import static ru.yandex.autotests.hwmorda.data.LgRubricData.TRAFFIC_URL;
import static ru.yandex.autotests.hwmorda.data.LgRubricData.TV_URL;
import static ru.yandex.autotests.hwmorda.data.LgRubricData.WEATHER_URL;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;


/**
 * User: alex89
 * Date: 12.09.12
 */
@Aqua.Test(title = "LG - главная")
@Features("LG")
@Stories("Main Page")
public class LgMainPageTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private LgSubPage lgSubPage = new LgSubPage(driver);
    private LgMainPage lgMainPage = new LgMainPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getLgBaseUrl());
        user.setsRegion(MOSCOW, CONFIG.getLgBaseUrl());
    }

    @Test
    public void weatherWidgetIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.weatherWidget);
        user.clicksOn(lgMainPage.weatherWidget);
        user.shouldSeePage(WEATHER_URL);
    }

    @Test
    public void newsWidgetIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.newsWidget);
        user.clicksOn(lgMainPage.newsWidget);
        user.shouldSeePage(TOPNEWS_URL);
    }

    @Test
    public void stocksWidgetIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.stocksWidget);
        user.clicksOn(lgMainPage.stocksWidget);
        user.shouldSeePage(STOCKS_URL);
    }

    @Test
    public void tvWidgetIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.tvWidget);
        user.clicksOn(lgMainPage.tvWidget);
        user.shouldSeePage(TV_URL);
    }

    @Test
    public void photoWidgetIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.photoWidget);
        user.clicksOn(lgMainPage.photoWidget);
        user.shouldSeePage(FOTKI_URL);
    }

    @Test
    public void trafficWidgetIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.trafficWidget);
        user.clicksOn(lgMainPage.trafficWidget);
        user.shouldSeePage(TRAFFIC_URL);
    }

    /////////////////////// Футер
    @Test
    public void weatherFooterButtonIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.footerPanel.weatherButton);
        user.clicksOn(lgMainPage.footerPanel.weatherButton);
        user.shouldSeePage(WEATHER_URL);
    }

    @Test
    public void newsFooterButtonIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.footerPanel.newsButton);
        user.clicksOn(lgMainPage.footerPanel.newsButton);
        user.shouldSeePage(TOPNEWS_URL);
    }

    @Test
    public void tvFooterButtonIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.footerPanel.tvButton);
        user.clicksOn(lgMainPage.footerPanel.tvButton);
        user.shouldSeePage(TV_URL);
    }

    @Test
    public void photoFooterButtonIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.footerPanel.photoButton);
        user.clicksOn(lgMainPage.footerPanel.photoButton);
        user.shouldSeePage(FOTKI_URL);
    }

    @Test
    public void logotypeIsCorrectOnLgMainPage() {
        user.shouldSeeElement(lgMainPage.logo);
        user.clicksOn(lgMainPage.logo);
        user.shouldSeePage(CONFIG.getLgBaseUrl());
    }
}