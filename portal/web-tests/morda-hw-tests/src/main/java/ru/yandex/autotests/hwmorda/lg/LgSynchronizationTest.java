package ru.yandex.autotests.hwmorda.lg;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.hwmorda.Properties;
import ru.yandex.autotests.hwmorda.pages.FotkiPage;
import ru.yandex.autotests.hwmorda.pages.LgMainPage;
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
 * Date: 14.09.12
 */
@Aqua.Test(title = "LG - синхронизация данных")
@Features("LG")
@Stories("Synchronization")
public class LgSynchronizationTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();

    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HwUserSteps userHW = new HwUserSteps(driver);
    private LgMainPage lgMainPage = new LgMainPage(driver);
    private FotkiPage fotkiPage = new FotkiPage(driver);
    private Client client = MordaClient.getJsonEnabledClient();
    private MordaClient mordaClient = new MordaClient(new BaseProperties.MordaEnv("www-rc"), CONFIG.getBaseDomain());

    @Before
    public void initLgMainPage() {
        user.opensPage(CONFIG.getLgBaseUrl());
        user.setsRegion(MOSCOW, CONFIG.getLgBaseUrl());
        mordaClient.cleanvarsActions(client).get();
        mordaClient.tuneActions(client).setRegion(CONFIG.getBaseDomain().getCapital());
    }

    @Test
    public void weatherSynchronization() {
        Weather weather = mordaClient.cleanvarsActions(client).get().getWeather();
        String text = "Погода\n" + weather.getT1() + "°\n" +
                weather.getT2Name() + " " + weather.getT2() + "°, " +
                weather.getT3Name() + " " + weather.getT3() + "°";
        user.opensPage(CONFIG.getLgBaseUrl());
        user.shouldSeeElement(lgMainPage.weatherWidget);
        user.shouldSeeElementWithText(lgMainPage.weatherWidget, text);
    }

    @Test
    public void firstNewsSynchronization() {
        TopnewsTabItem newsItem = mordaClient.cleanvarsActions(client).get().getTopnews().getTabs().get(0).getNews().get(0);
        String text = "Новости\n" + newsItem.getText() + newsItem.getHreftext();
        user.opensPage(CONFIG.getLgBaseUrl());
        user.shouldSeeElement(lgMainPage.newsWidget);
        user.shouldSeeElementWithText(lgMainPage.newsWidget, text);
    }

    @Test
    public void trafficSynchronization() {
        Traffic traffic = mordaClient.cleanvarsActions(client).get().getTraffic();
        String traffictext = "Пробки\n " + traffic.getRate() + " " + traffic.getRateaccus() +
                (traffic.getDown() != null ? "↓" : (traffic.getUp() != null ? "↑" : "")) +
                (traffic.getDescr() != null ?"\n" + traffic.getDescr() : "");
        user.opensPage(CONFIG.getLgBaseUrl());
        user.shouldSeeElement(lgMainPage.trafficWidget);
        user.shouldSeeElementWithText(lgMainPage.trafficWidget, traffictext);
    }

//    @Test
//    public void stocksSynchronization() {
//        StocksBlock stocksBlock = mordaClient.cleanvarsActions(client).get(UserAgent.TOUCH).getStocks();
//        List<String> stocksTexts = new ArrayList<>();
//        stocksTexts.add("Котировки");
//        for (Row stockRow : stocksBlock.getBlocks().get(0).getRows()) {
//            stocksTexts.add(stockRow.getText().replace(" ", " ") + " " + stockRow.getData().get(0).getValue2());
//        }
//        String stockstext = StringUtils.join(stocksTexts, '\n');
//        user.opensPage(CONFIG.getLgBaseUrl());
//        user.shouldSeeElement(lgMainPage.stocksWidget);
//        user.shouldSeeElementWithText(lgMainPage.stocksWidget, stockstext);
//    }

    @Test
    public void photoSynchronization() {
        user.opensPage(CONFIG.getFotkiBaseUrl());
        user.shouldSeeElement(fotkiPage.foto);
        String fotoSrc = userHW.getFotoSrc();
        user.opensPage(CONFIG.getLgBaseUrl());
        user.shouldSeeElement(lgMainPage.photoWidget);
        user.shouldSeeElement(lgMainPage.photoInPhotoWidget);
    }
}
