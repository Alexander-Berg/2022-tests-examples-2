package ru.yandex.autotests.morda.monitorings.topnews;

import org.apache.commons.httpclient.util.HttpURLConnection;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.topnews.Topnews;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsStocksItem;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTab;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTabItem;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.mordabackend.stocks.StockUtils;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.flatten;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.getTabsCountMatcher;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.utils.morda.region.Region.ALMATY;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.CHEBOKSARI;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.DNEPROPETROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.DONECK;
import static ru.yandex.autotests.utils.morda.region.Region.DUBNA;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.HABAROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.IRKUTSK;
import static ru.yandex.autotests.utils.morda.region.Region.KALININGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.KRASNODAR;
import static ru.yandex.autotests.utils.morda.region.Region.KRASNOYARSK;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.MURMANSK;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.PETROZAVODSK;
import static ru.yandex.autotests.utils.morda.region.Region.ROSTOV_NA_DONU;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.SEVASTOPOL;
import static ru.yandex.autotests.utils.morda.region.Region.SIMFEROPOL;
import static ru.yandex.autotests.utils.morda.region.Region.TOLYATTI;
import static ru.yandex.autotests.utils.morda.region.Region.TOMSK;
import static ru.yandex.autotests.utils.morda.region.Region.TULA;
import static ru.yandex.autotests.utils.morda.region.Region.UFA;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIKAVKAZ;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIVOSTOK;
import static ru.yandex.autotests.utils.morda.region.Region.VOLGOGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.VORONEZH;
import static ru.yandex.autotests.utils.morda.region.Region.YAROSLAVL;

@Aqua.Test(title = "Новости")
@Features("Новости")
@RunWith(Parameterized.class)
public class TopnewsTest {

    private static final MonitoringProperties CONFIG = new MonitoringProperties();

    @Rule
    public MordaMonitoringsRule rule = new MordaMonitoringsRule();

    @Parameterized.Parameters(name = "Topnews block in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
                ASTANA, ALMATY, CHEBOKSARI, CHELYABINSK, DNEPROPETROVSK, DONECK, EKATERINBURG,
                HABAROVSK, IRKUTSK, HARKOV, KALININGRAD, KRASNODAR, KRASNOYARSK, KIEV, KAZAN,
                MINSK, MURMANSK, MOSCOW, NIZHNIY_NOVGOROD, NOVOSIBIRSK, PERM, PETROZAVODSK,
                ROSTOV_NA_DONU, SEVASTOPOL, SIMFEROPOL, SAMARA, SANKT_PETERBURG, TOMSK, TOLYATTI,
                TULA, UFA, VLADIKAVKAZ, VLADIVOSTOK, VOLGOGRAD, VORONEZH, YAROSLAVL, DUBNA
        ));
    }

    private Region region;
    private Cleanvars cleanvars;
    private Client client;

    public TopnewsTest(Region region) throws IOException {
        this.region = region;
        this.client = MordaClient.getJsonEnabledClient();

        MordaClient mordaClient = new MordaClient(CONFIG.getMordaEnv(), region.getDomain());
        mordaClient.rapidoActions(client)
                .get("topnews", new CookieHeader(new Cookie(CookieName.
                        YANDEX_GID, region.getRegionId())));

        mordaClient.tuneActions(client).setRegion(region);

        String response = mordaClient
                .rapidoActions(client)
                .getResponse("topnews", null, null, null, null)
                .readEntity(String.class);

        this.cleanvars = MordaClient.getObjectMapper().readValue(response, Cleanvars.class);

        rule.addMeta("json", response);
    }

    @Test
    public void topnewsAreShown() {
        shouldHaveParameter("Новости отсутствуют в " + region.getName(),
                cleanvars.getTopnews(), having(on(Topnews.class).getProcessed(), equalTo(1)));

        shouldHaveParameter("Новости отсутствуют в " + region.getName(),
                cleanvars.getTopnews(), having(on(Topnews.class).getShow(), equalTo(1)));
    }

    @Test
    public void topnewsTabsCount() throws IOException {
        ifTopnewsShown();

        shouldHaveParameter("Слишком мало табов в новостях в " + region.getName(),
                cleanvars.getTopnews(), having(on(Topnews.class).getTabs(),
                        hasSize(getTabsCountMatcher(region))));

        for (TopnewsTab tab : cleanvars.getTopnews().getTabs()) {
            if (!tab.getKey().equals("news")) {

                shouldHaveParameter(tab, having(on(TopnewsTab.class).getHref(), not(isEmptyOrNullString())));
                shouldHaveResponseCode(client, tab.getHref(), equalTo(HttpURLConnection.HTTP_OK));

            }
        }

    }

    @Test
    public void topnewsCount() {
        ifTopnewsShown();

        for (TopnewsTab topnewsTab : cleanvars.getTopnews().getTabs()) {
            shouldHaveParameter("Слишком мало новостей в табе в " + region.getName(),
                    topnewsTab, having(on(TopnewsTab.class).getNews(), hasSize(equalTo(5))));
        }
    }

    @Test
    public void topnewsItemsResponse() throws IOException {
        ifTopnewsShown();

        shouldHaveParameter(cleanvars.getTopnews(), having(on(Topnews.class).getHref(), not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getTopnews().getHref(), equalTo(HttpURLConnection.HTTP_OK));

        List<TopnewsTabItem> allNews =
                flatten(extract(cleanvars.getTopnews().getTabs(), on(TopnewsTab.class).getNews()));

        for (TopnewsTabItem topnewsTabItem : allNews) {

            shouldHaveParameter(topnewsTabItem, having(on(TopnewsTabItem.class).getHreftext(),
                    not(isEmptyOrNullString())));
            shouldHaveParameter(topnewsTabItem, having(on(TopnewsTabItem.class).getHref(), not(isEmptyOrNullString())));
            shouldHaveResponseCode(client, topnewsTabItem.getHref(), equalTo(HttpURLConnection.HTTP_OK));

        }
    }

    @Test
    public void topnewsPromoResponse() throws IOException {
        ifTopnewsShown();
        ifTopnewsPromoExists();

        shouldHaveParameter(cleanvars.getTopnews(), having(on(Topnews.class).getPromotext(),
                not(isEmptyOrNullString())));
        shouldHaveParameter(cleanvars.getTopnews(), having(on(Topnews.class).getPromohref(),
                not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getTopnews().getPromohref(), equalTo(HttpURLConnection.HTTP_OK));

    }

    @Test
    @Ignore("Waiting https://st.yandex-team.ru/TESTPORTAL-732")
    public void topnewsStocksItems() throws IOException {
        ifTopnewsShown();
        ifTopnewsStocksExist();

        for (TopnewsStocksItem topnewsStocksItem : cleanvars.getTopnews().getTopnewsStocks()) {

            shouldHaveParameter(topnewsStocksItem, having(on(TopnewsStocksItem.class).getAlt(),
                    not(isEmptyOrNullString())));
            shouldHaveParameter(topnewsStocksItem, having(on(TopnewsStocksItem.class).getId(),
                    not(isEmptyOrNullString())));
            shouldHaveParameter(topnewsStocksItem, having(on(TopnewsStocksItem.class).getText(),
                    not(isEmptyOrNullString())));
            shouldHaveParameter(topnewsStocksItem, having(on(TopnewsStocksItem.class).getText(),
                    not(isEmptyOrNullString())));
            shouldHaveParameter(topnewsStocksItem, having(on(TopnewsStocksItem.class).getValue(),
                    StockUtils.VALUE_SHORT_MATCHER));

            if (!isEmptyOrNullString().matches(topnewsStocksItem.getDelta())) {
                shouldHaveParameter(topnewsStocksItem, having(on(TopnewsStocksItem.class).getDelta(),
                        StockUtils.DELTA_SHORT_MATCHER));
            }

            shouldHaveParameter(topnewsStocksItem, having(on(TopnewsStocksItem.class).getHref(),
                    not(isEmptyOrNullString())));

            shouldHaveResponseCode(client, topnewsStocksItem.getHref(), equalTo(HttpURLConnection.HTTP_OK));

        }

    }

    private void ifTopnewsShown() {
        assumeThat("Новости отсутствуют в " + region.getName(), cleanvars.getTopnews(),
                having(on(Topnews.class).getShow(), equalTo(1)));
    }

    private void ifTopnewsStocksExist() {
        assumeThat("Котировки в новостях отсутствуют в " + region.getName(), cleanvars.getTopnews(),
                having(on(Topnews.class).getTopnewsStocks(), hasSize(greaterThan(0))));
    }

    private void ifTopnewsPromoExists() {
        assumeThat("Промо отсутствует в " + region.getName(), cleanvars.getTopnews(),
                having(on(Topnews.class).getPromotext(), notNullValue()));
    }
}
