package ru.yandex.autotests.morda.monitorings.appearance;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.afisha.Afisha;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.etrains.Etrains;
import ru.yandex.autotests.mordabackend.beans.topnews.Topnews;
import ru.yandex.autotests.mordabackend.beans.traffic.Traffic;
import ru.yandex.autotests.mordabackend.beans.tv.Tv;
import ru.yandex.autotests.mordabackend.beans.weather.Weather;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.exists;

@Aqua.Test(title = "Блоки Морды в браузере")
@Features("Блоки Морды в браузере")
@RunWith(Parameterized.class)
public class AppearanceInBrowserTest {

    private static final MonitoringProperties CONFIG = new MonitoringProperties();
    private MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule(DesiredCapabilities.firefox());
    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private MordaMonitoringsRule mordaMonitoringsRule = new MordaMonitoringsRule(driver);
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private Region region;
    private Cleanvars cleanvars;
    private Client client;

    public AppearanceInBrowserTest(Region region) throws IOException {
        this.region = region;
        this.client = MordaClient.getJsonEnabledClient();

        MordaClient mordaClient = new MordaClient(CONFIG.getMordaEnv(), region.getDomain());
        mordaClient.rapidoActions(client)
                .getAllResponse(new CookieHeader(new Cookie(CookieName.
                        YANDEX_GID, region.getRegionId())), null, null, null);

        mordaClient.tuneActions(client).setRegion(region);

        String response = mordaClient
                .rapidoActions(client)
                .getAllResponse(null, null, null, null)
                .readEntity(String.class);

        this.cleanvars = MordaClient.getObjectMapper().readValue(response, Cleanvars.class);

        System.out.println(cleanvars);

        mordaMonitoringsRule.addMeta("json", response);
    }

    @Parameterized.Parameters(name = "Blocks in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
                MOSCOW, ASTANA, MINSK, KIEV
        ));
    }

    @Rule
    public MordaAllureBaseRule getRule() {
        return mordaAllureBaseRule.withRule(mordaMonitoringsRule);
    }

    @Test
    public void afishaAppearance() {
        ifAfishaShown();

        BasePage page = new BasePage(driver);
        user.opensPage("https://" + CONFIG.getMordaEnv() + ".yandex" + region.getDomain());
        user.setsRegion(region);

        user.shouldSeeElement(page.afishaBlock);
        if (exists().matches(page.afishaBlock.afishaTab)) {
            user.shouldSeeElement(page.afishaBlock.afishaTab);
            user.clicksOn(page.afishaBlock.afishaTab);
        } else {
            user.shouldSeeElement(page.afishaBlock.afishaTitle);
        }
        user.shouldSeeListWithSize(page.afishaBlock.afishaEvents, greaterThan(0));

    }

    @Test
    public void topnewsAppearance() {
        ifTopnewsShown();

        BasePage page = new BasePage(driver);
        user.opensPage("https://" + CONFIG.getMordaEnv() + ".yandex" + region.getDomain());
        user.setsRegion(region);

        user.shouldSeeElement(page.newsBlock);
        user.shouldSeeElement(page.newsBlock.mainNewsTab);
        user.shouldSeeListWithSize(page.newsBlock.mainNews, greaterThan(0));

    }

    @Test
    public void etrainsAppearance() {
        ifEtrainsAreShown();

        MainPage page = new MainPage(driver);
        user.opensPage("https://" + CONFIG.getMordaEnv() + ".yandex" + region.getDomain());
        user.setsRegion(region);

        user.shouldSeeElement(page.etrainsBlock);
        user.shouldSeeElement(page.etrainsBlock.eHeader);

    }

    @Test
    public void tvAppearance() {
        ifTvShown();

        MainPage page = new MainPage(driver);
        user.opensPage("https://" + CONFIG.getMordaEnv() + ".yandex" + region.getDomain());
        user.setsRegion(region);

        user.shouldSeeElement(page.tvBlock);
        if (exists().matches(page.tvBlock.tvTab)) {
            user.shouldSeeElement(page.tvBlock.tvTab);
        } else {
            user.shouldSeeElement(page.tvBlock.tvTitle);
        }

        user.shouldSeeListWithSize(page.tvBlock.tvEvents, greaterThan(0));

    }

    @Test
    public void trafficAppearance() {
        ifTrafficShown();

        MainPage page = new MainPage(driver);
        user.opensPage("https://" + CONFIG.getMordaEnv() + ".yandex" + region.getDomain());
        user.setsRegion(region);

        user.shouldSeeElement(page.trafficFullBlock);
        user.shouldSeeElement(page.trafficFullBlock.trafficLink);
        user.shouldSeeElement(page.trafficFullBlock.trafficLights);
    }

    @Test
    public void weatherAppearance() {
        ifWeatherShown();

        MainPage page = new MainPage(driver);
        user.opensPage("https://" + CONFIG.getMordaEnv() + ".yandex" + region.getDomain());
        user.setsRegion(region);

        user.shouldSeeElement(page.weatherBlock);
        user.shouldSeeElement(page.weatherBlock.weatherBlockHeader);
        user.shouldSeeElement(page.weatherBlock.weatherBlockHeader.weatherLink);
        user.shouldSeeElement(page.weatherBlock.weatherBlockHeader.weatherIcon);
        user.shouldSeeElement(page.weatherBlock.weatherForecast);
    }

    private void ifAfishaShown() {
        assumeThat("Афиша отсутствует в " + region.getName(), cleanvars.getAfisha(),
                having(on(Afisha.class).getShow(), equalTo(1)));
    }

    private void ifTopnewsShown() {
        assumeThat("Новости отсутствуют в " + region.getName(), cleanvars.getTopnews(),
                having(on(Topnews.class).getShow(), equalTo(1)));
    }

    private void ifTvShown() {
        assumeThat("ТВ отсутствует в " + region.getName(), cleanvars.getTV(),
                having(on(Tv.class).getShow(), equalTo(1)));
    }

    private void ifEtrainsAreShown() {
        assumeThat("Электрички отсутствуют в " + region.getName(), cleanvars.getEtrains(),
                having(on(Etrains.class).getShow(), equalTo(1)));
    }

    private void ifTrafficShown() {
        assumeThat("Пробки отсутствуют в " + region.getName(), cleanvars.getTraffic(),
                having(on(Traffic.class).getShow(), equalTo(1)));
    }

    private void ifWeatherShown() {
        assumeThat("Погода отсутствует в " + region.getName(), cleanvars.getWeather(),
                having(on(Weather.class).getShow(), equalTo(1)));
    }

}
