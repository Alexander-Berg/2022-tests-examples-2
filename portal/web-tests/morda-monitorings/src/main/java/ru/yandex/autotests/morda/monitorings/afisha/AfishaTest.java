package ru.yandex.autotests.morda.monitorings.afisha;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.afisha.Afisha;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaEvent;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaPremiereEvent;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.util.Arrays;
import java.util.Collection;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
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
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.CHEBOKSARI;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.DNEPROPETROVSK;
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

@Aqua.Test(title = "Афиша")
@Features("Афиша")
@RunWith(Parameterized.class)
public class AfishaTest {
    private static final MonitoringProperties CONFIG = new MonitoringProperties();

    @Rule
    public MordaMonitoringsRule rule = new MordaMonitoringsRule();
    private Region region;
    private Cleanvars cleanvars;
    private Client client;

    public AfishaTest(Region region) throws IOException {
        this.region = region;
        this.client = MordaClient.getJsonEnabledClient();

        MordaClient mordaClient = new MordaClient(CONFIG.getMordaEnv(), region.getDomain());
        mordaClient.rapidoActions(client)
                .get("afisha", new CookieHeader(new Cookie(CookieName.
                        YANDEX_GID, region.getRegionId())));

        mordaClient.tuneActions(client).setRegion(region);

        String response = mordaClient
                .rapidoActions(client)
                .getResponse("afisha", null, null, null, null)
                .readEntity(String.class);

        this.cleanvars = MordaClient.getObjectMapper().readValue(response, Cleanvars.class);
        rule.addMeta("json", response);
    }

    @Parameterized.Parameters(name = "Afisha block in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
                ASTANA, ALMATY, CHEBOKSARI, CHELYABINSK, DNEPROPETROVSK, EKATERINBURG,
                HABAROVSK, IRKUTSK, HARKOV, KALININGRAD, KRASNODAR, KRASNOYARSK, KIEV, KAZAN,
                MINSK, MURMANSK, MOSCOW, NIZHNIY_NOVGOROD, NOVOSIBIRSK, PERM, PETROZAVODSK,
                ROSTOV_NA_DONU, SEVASTOPOL, SIMFEROPOL, SAMARA, SANKT_PETERBURG, TOMSK, TOLYATTI,
                TULA, UFA, VLADIKAVKAZ, VLADIVOSTOK, VOLGOGRAD, VORONEZH, YAROSLAVL, DUBNA
        ));
    }

    @Test
    public void afishaIsShown() {
        shouldHaveParameter("Афиша отсутствует в " + region.getName(),
                cleanvars.getAfisha(), having(on(Afisha.class).getProcessed(), equalTo(1)));

        shouldHaveParameter("Афиша отсутствует в " + region.getName(),
                cleanvars.getAfisha(), having(on(Afisha.class).getShow(), equalTo(1)));
    }

    @Test
    public void afishaEventsCount() {
        ifAfishaShown();

        int events = cleanvars.getAfisha().getEvents().size();

        assertThat("Слишком мало событий афиши в " + region.getName(), events, greaterThanOrEqualTo(3));
    }

    @Test
    public void afishaEvents() throws IOException {
        ifAfishaShown();

        shouldHaveParameter(cleanvars.getAfisha(), having(on(Afisha.class).getHref(), notNullValue()));
        shouldHaveResponseCode(client, cleanvars.getAfisha().getHref(), equalTo(HttpURLConnection.HTTP_OK));

        for (AfishaEvent afishaEvent : cleanvars.getAfisha().getEvents()) {

            shouldHaveParameter(afishaEvent, having(on(AfishaEvent.class).getName(), not(isEmptyOrNullString())));
            shouldHaveParameter(afishaEvent, having(on(AfishaEvent.class).getHref(), notNullValue()));
            shouldHaveResponseCode(client, afishaEvent.getHref(), equalTo(HttpURLConnection.HTTP_OK));

        }
    }

    @Test
    public void afishaPromo() throws IOException {
        ifAfishaShown();
        ifPromoExists();

        shouldHaveParameter(cleanvars.getAfisha(), having(on(Afisha.class).getPromo().getText(),
                not(isEmptyOrNullString())));

        shouldHaveParameter(cleanvars.getAfisha(), having(on(Afisha.class).getPromo().getUrlHttps(), notNullValue()));
        shouldHaveResponseCode(client, cleanvars.getAfisha().getPromo().getUrlHttps(), equalTo(HttpURLConnection.HTTP_OK));
    }

    @Test
    public void afishaPremiersResponse() throws IOException {
        ifAfishaShown();
        ifPremiereExists();

        AfishaPremiereEvent afishaPremiereEvent = cleanvars.getAfisha().getPremiere();

        shouldHaveParameter(afishaPremiereEvent, having(on(AfishaPremiereEvent.class).getName(),
                not(isEmptyOrNullString())));
        shouldHaveParameter(afishaPremiereEvent, having(on(AfishaPremiereEvent.class).getHref(), notNullValue()));
        shouldHaveResponseCode(client, afishaPremiereEvent.getHref(), equalTo(HttpURLConnection.HTTP_OK));

    }

    private void ifAfishaShown() {
        assumeThat("Афиша отсутствует в " + region.getName(), cleanvars.getAfisha(),
                having(on(Afisha.class).getShow(), equalTo(1)));
    }

    private void ifPromoExists() {
        assumeThat("Промо Афиши отсутствует в " + region.getName(), cleanvars.getAfisha(),
                having(on(Afisha.class).getPromo(), notNullValue()));
    }

    private void ifPremiereExists() {
        assumeThat("Премьеры Афиши отсутствуют в " + region.getName(), cleanvars.getAfisha(),
                having(on(Afisha.class).getPremiere(), hasSize(greaterThan(0))));
    }
}
