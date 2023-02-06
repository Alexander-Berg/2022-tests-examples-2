package ru.yandex.autotests.turkey.informers;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.turkey.data.InformersData.REGION_LINK;
import static ru.yandex.autotests.turkey.data.InformersData.TRAFFIC_LINK;
import static ru.yandex.autotests.turkey.data.InformersData.USD_LINK;
import static ru.yandex.autotests.turkey.data.InformersData.EUR_LINK;
import static ru.yandex.autotests.turkey.data.InformersData.WEATHER_LINK;

/**
 * User: ivannik
 * Date: 14.09.2014
 */
@Aqua.Test(title = "Информеры над футером")
@Features("Informers")
@Stories("Informers")
public class InformersTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.shouldSeeElement(yandexComTrPage.informersBlock);
    }

    @Test
    public void regionInformer() {
        user.shouldSeeElement(yandexComTrPage.informersBlock.regionInformerLink);
        user.shouldSeeLink(yandexComTrPage.informersBlock.regionInformerLink, REGION_LINK);
    }

    @Test
    public void weatherInformer() {
        user.shouldSeeElement(yandexComTrPage.informersBlock.weatherInformerLink);
        user.shouldSeeElement(yandexComTrPage.informersBlock.weatherInformerLink.icon);
        user.shouldSeeLink(yandexComTrPage.informersBlock.weatherInformerLink, WEATHER_LINK);
    }

    @Test
    public void trafficInformer() {
        user.shouldSeeElement(yandexComTrPage.informersBlock.trafficInformerLink);
        user.shouldSeeElement(yandexComTrPage.informersBlock.trafficInformerLink.icon);
        user.shouldSeeLink(yandexComTrPage.informersBlock.trafficInformerLink, TRAFFIC_LINK);
    }

    @Test
    public void stocksUSDInformer() {
        user.shouldSeeElement(yandexComTrPage.informersBlock.USDInformerLink);
        user.shouldSeeLink(yandexComTrPage.informersBlock.USDInformerLink, USD_LINK);
    }

    @Test
    public void stocksEURInformer() {
        user.shouldSeeElement(yandexComTrPage.informersBlock.EURInformerLink);
        user.shouldSeeLink(yandexComTrPage.informersBlock.EURInformerLink, EUR_LINK);
    }
}
