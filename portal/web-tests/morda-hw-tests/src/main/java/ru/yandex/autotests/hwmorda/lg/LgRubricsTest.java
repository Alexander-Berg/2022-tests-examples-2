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
@Aqua.Test(title = "LG - рубрики")
@Features("LG")
@Stories("Rubrics")
public class LgRubricsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();

    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private LgSubPage lgSubPage = new LgSubPage(driver);
    private LgMainPage lgMainPage = new LgMainPage(driver);

    @Before
    public void initLgMainPage() {
        user.opensPage(CONFIG.getLgBaseUrl());
        user.setsRegion(MOSCOW, CONFIG.getLgBaseUrl());
    }

    @Test
    public void weatherRubricIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(TRAFFIC_URL);
        user.clicksOn(lgSubPage.rubricsPanel.weatherButton);
        user.shouldSeeElementIsSelected(lgSubPage.rubricsPanel.weatherButton);
        user.shouldSeeElement(lgSubPage.weatherWidget);
        user.shouldSeePage(WEATHER_URL);
    }

    @Test
    public void newsRubricIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(TRAFFIC_URL);
        user.clicksOn(lgSubPage.rubricsPanel.newsButton);
        user.shouldSeeElementIsSelected(lgSubPage.rubricsPanel.newsButton);
        user.shouldSeeElement(lgSubPage.newsWidget);
        user.shouldSeePage(TOPNEWS_URL);
    }

    @Test
    public void stocksRubricIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(TRAFFIC_URL);
        user.clicksOn(lgSubPage.rubricsPanel.stocksButton);
        user.shouldSeeElementIsSelected(lgSubPage.rubricsPanel.stocksButton);
        user.shouldSeeElement(lgSubPage.stocksWidget);
        user.shouldSeePage(STOCKS_URL);
    }

    @Test
    public void tvRubricIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(TRAFFIC_URL);
        user.clicksOn(lgSubPage.rubricsPanel.tvButton);
        user.shouldSeeElementIsSelected(lgSubPage.rubricsPanel.tvButton);
        user.shouldSeeElement(lgSubPage.tvWidget);
        user.shouldSeePage(TV_URL);
    }

    @Test
    public void photoRubricIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(TRAFFIC_URL);
        user.clicksOn(lgSubPage.rubricsPanel.photoButton);
        user.shouldSeeElementIsSelected(lgSubPage.rubricsPanel.photoButton);
        user.shouldSeeElement(lgSubPage.photoWidget);
        user.shouldSeePage(FOTKI_URL);
    }

    @Test
    public void trafficRubricIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(FOTKI_URL);
        user.clicksOn(lgSubPage.rubricsPanel.trafficButton);
        user.shouldSeeElementIsSelected(lgSubPage.rubricsPanel.trafficButton);
        user.shouldSeeElement(lgSubPage.trafficWidget);
        user.shouldSeePage(TRAFFIC_URL);
    }

    ////переключалки в Футере:
    @Test
    public void regionalNewsIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(TOPNEWS_URL);
        user.shouldSeeElement(lgSubPage.footerPanel.regionalNewsButton);
        user.clicksOn(lgSubPage.footerPanel.regionalNewsButton);
        user.shouldSeeElement(lgSubPage.regNewsWidget);
        user.shouldSeePage(TOPNEWS_URL);

        user.shouldSeeElement(lgSubPage.footerPanel.mainNewsButton);
        user.clicksOn(lgSubPage.footerPanel.mainNewsButton);
        user.shouldSeeElement(lgSubPage.newsWidget);
        user.shouldSeePage(TOPNEWS_URL);
    }

    @Test
    public void slideShowIsSwitchedCorrectlyOnLgSubPage() {
        user.opensPage(FOTKI_URL);
        user.shouldSeeElement(lgSubPage.footerPanel.slideShowButton);
        user.shouldNotSeeElement(lgSubPage.slideShowMode);
        user.clicksOn(lgSubPage.footerPanel.slideShowButton);
        user.shouldSeeElement(lgSubPage.slideShowMode);
        user.shouldSeeElement(lgSubPage.photoWidget);
        user.shouldSeePage(FOTKI_URL);

        user.clicksOn(lgSubPage.anyPlace);

        user.shouldSeeElement(lgSubPage.photoWidget);
        user.shouldNotSeeElement(lgSubPage.slideShowMode);
        user.shouldSeePage(FOTKI_URL);
    }

}