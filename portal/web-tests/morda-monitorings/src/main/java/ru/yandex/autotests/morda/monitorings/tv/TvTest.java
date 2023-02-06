package ru.yandex.autotests.morda.monitorings.tv;

import org.apache.commons.httpclient.util.HttpURLConnection;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.tv.Tv;
import ru.yandex.autotests.mordabackend.beans.tv.TvAnnounce;
import ru.yandex.autotests.mordabackend.beans.tv.TvEvent;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
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
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.utils.morda.region.Region.ALMATY;
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

@Aqua.Test(title = "ТВ")
@Features("ТВ")
@RunWith(Parameterized.class)
public class TvTest {

    private static final MonitoringProperties CONFIG = new MonitoringProperties();

    @Rule
    public MordaMonitoringsRule rule = new MordaMonitoringsRule();

    @Parameterized.Parameters(name = "Tv block in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
                ALMATY, CHEBOKSARI, CHELYABINSK, DNEPROPETROVSK, DONECK, EKATERINBURG,
                HABAROVSK, IRKUTSK, HARKOV, KALININGRAD, KRASNODAR, KRASNOYARSK, KIEV, KAZAN,
                MINSK, MURMANSK, MOSCOW, NIZHNIY_NOVGOROD, NOVOSIBIRSK, PERM, PETROZAVODSK,
                ROSTOV_NA_DONU, SEVASTOPOL, SIMFEROPOL, SAMARA, SANKT_PETERBURG, TOMSK, TOLYATTI,
                TULA, UFA, VLADIKAVKAZ, VLADIVOSTOK, VOLGOGRAD, VORONEZH, YAROSLAVL, DUBNA
        ));
    }

    private Region region;
    private Cleanvars cleanvars;
    private Client client;

    public TvTest(Region region) throws IOException {
        this.region = region;
        this.client = MordaClient.getJsonEnabledClient();

        MordaClient mordaClient = new MordaClient(CONFIG.getMordaEnv(), region.getDomain());
        mordaClient.rapidoActions(client)
                .get("tv", new CookieHeader(new Cookie(CookieName.
                        YANDEX_GID, region.getRegionId())));

        mordaClient.tuneActions(client).setRegion(region);

        String response = mordaClient
                .rapidoActions(client)
                .getResponse("tv", null, null, null, null)
                .readEntity(String.class);

        this.cleanvars = MordaClient.getObjectMapper().readValue(response, Cleanvars.class);

        rule.addMeta("json", response);
    }

    @Test
    public void tvIsShown() {
        shouldHaveParameter("Тв отсутствует в " + region.getName(),
                cleanvars.getTV(), having(on(Tv.class).getProcessed(), equalTo(1)));

        shouldHaveParameter("Тв отсутствует в " + region.getName(),
                cleanvars.getTV(), having(on(Tv.class).getShow(), equalTo(1)));
    }

    @Test
    public void tvEventsCount() {
        ifTvShown();

        shouldHaveParameter("Слишком мало событий тв в " + region.getName(),
                cleanvars.getTV(), having(on(Tv.class).getProgramms(), hasSize(greaterThanOrEqualTo(2))));
    }

    @Test
    public void tvEventsResponse() throws IOException {
        ifTvShown();

        shouldHaveParameter(cleanvars.getTV(), having(on(Tv.class).getHref(), notNullValue()));
        shouldHaveResponseCode(client, cleanvars.getTV().getHref(), equalTo(HttpURLConnection.HTTP_OK));

        for (TvEvent tvEvent : cleanvars.getTV().getProgramms()) {

            shouldHaveParameter(tvEvent, having(on(TvEvent.class).getName(), not(isEmptyOrNullString())));

            shouldHaveParameter(tvEvent, having(on(TvEvent.class).getHref(), notNullValue()));
            shouldHaveResponseCode(client, tvEvent.getHref(), equalTo(HttpURLConnection.HTTP_OK));

        }
    }

    @Test
    public void tvAnnouncesResponse() throws IOException {
        ifTvShown();
        ifTvAnnounceExists();

        for (TvAnnounce tvAnnounce : cleanvars.getTV().getAnnounces()) {

            shouldHaveParameter(tvAnnounce, having(on(TvAnnounce.class).getText(), not(isEmptyOrNullString())));
            shouldHaveParameter(tvAnnounce, having(on(TvAnnounce.class).getUrl(), notNullValue()));
            shouldHaveResponseCode(client, tvAnnounce.getUrl(), equalTo(HttpURLConnection.HTTP_OK));

        }
    }

    private void ifTvShown() {
        assumeThat("ТВ отсутствует в " + region.getName(), cleanvars.getTV(),
                having(on(Tv.class).getShow(), equalTo(1)));
    }

    private void ifTvAnnounceExists() {
        assumeThat("ТВ анонсы отсутствуют в " + region.getName(), cleanvars.getTV(),
                having(on(Tv.class).getAnnounces(), hasSize(greaterThan(0))));
    }
}
