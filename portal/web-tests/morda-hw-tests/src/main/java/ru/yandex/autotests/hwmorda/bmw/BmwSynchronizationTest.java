package ru.yandex.autotests.hwmorda.bmw;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.hwmorda.Properties;
import ru.yandex.autotests.hwmorda.pages.BmwPage;
import ru.yandex.autotests.hwmorda.steps.HwUserSteps;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTabItem;
import ru.yandex.autotests.mordabackend.beans.traffic.Traffic;
import ru.yandex.autotests.mordabackend.beans.weather.Weather;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: alex89
 * Date: 13.09.12
 */

@Aqua.Test(title = "BMW - синхронизация данных")
@Features("Bmw")
@Stories("Synchronization")
public class BmwSynchronizationTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HwUserSteps userHW = new HwUserSteps(driver);
    private BmwPage bmwPage = new BmwPage(driver);
    private Client client = MordaClient.getJsonEnabledClient();
    private MordaClient mordaClient = new MordaClient(new BaseProperties.MordaEnv("www-rc"), CONFIG.getBaseDomain());

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBMWBaseUrl());
        user.setsRegion(MOSCOW, CONFIG.getBMWBaseUrl());
        mordaClient.cleanvarsActions(client).get();
        mordaClient.tuneActions(client).setRegion(CONFIG.getBaseDomain().getCapital());
    }

    @Test
    public void weatherSynchronization() {
        Weather weather = mordaClient.cleanvarsActions(client).get().getWeather();
        String text = weather.getT1().replace("−", "-") + "°\n" +
                weather.getT2Name() + " " + weather.getT2().replace("−", "-") + "°, " +
                weather.getT3Name() + " " + weather.getT3().replace("−", "-") + "°";
        user.opensPage(CONFIG.getBMWBaseUrl());
        user.shouldSeeElement(bmwPage.weatherButton);
        user.shouldSeeElementWithText(bmwPage.weatherButton, text);
    }

    @Test
    public void firstNewsSynchronization() {
        TopnewsTabItem newsItem = mordaClient.cleanvarsActions(client).get().getTopnews().getTabs().get(0).getNews().get(0);
        String text = newsItem.getText() + newsItem.getHreftext();
        user.opensPage(CONFIG.getBMWBaseUrl());
        user.shouldSeeElement(bmwPage.newsButton);
        user.shouldSeeElementWithText(bmwPage.newsButton, text);
    }

    @Test
    public void trafficSynchronization() {
        Traffic traffic = mordaClient.cleanvarsActions(client).get().getTraffic();
        String text = traffic.getRate() + traffic.getRateaccus() +
                (traffic.getDescr() != null ? "\n" + traffic.getDescr() : "");
        user.opensPage(CONFIG.getBMWBaseUrl());
        user.shouldSeeElement(bmwPage.trafficButton);
        user.shouldSeeElementWithText(bmwPage.trafficButton, text);
    }

//    @Test
//    public void stocksSynchronization() {
//        StocksBlock stocksBlock = mordaClient.cleanvarsActions(client).get(UserAgent.TOUCH).getStocks();
//        List<String> stocksTexts = new ArrayList<>();
//        for (Row stockRow : stocksBlock.getBlocks().get(0).getRows()) {
//            stocksTexts.add(stockRow.getText().replace(" ", " "));
//            stocksTexts.add(stockRow.getData().get(0).getValue2());
//        }
//        String text = StringUtils.join(stocksTexts, '\n');
//        user.opensPage(CONFIG.getBMWBaseUrl());
//        user.shouldSeeElement(bmwPage.stocksArea);
//        user.shouldSeeElementWithText(bmwPage.stocksArea, text);
//    }
}