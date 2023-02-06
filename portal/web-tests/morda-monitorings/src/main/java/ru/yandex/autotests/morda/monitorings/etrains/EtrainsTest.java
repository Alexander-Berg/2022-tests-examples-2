package ru.yandex.autotests.morda.monitorings.etrains;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.monitorings.MonitoringProperties;
import ru.yandex.autotests.morda.monitorings.rules.MordaMonitoringsRule;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.etrains.EtrainItem;
import ru.yandex.autotests.mordabackend.beans.etrains.Etrains;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.cookie.CookieName;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.utils.morda.region.Region.ATBASAR;
import static ru.yandex.autotests.utils.morda.region.Region.BROVARY;
import static ru.yandex.autotests.utils.morda.region.Region.DUBNA;
import static ru.yandex.autotests.utils.morda.region.Region.ORSHA;
import static ru.yandex.autotests.utils.morda.region.Region.VYBORG;

@Aqua.Test(title = "Электрички")
@Features("Электрички")
@RunWith(Parameterized.class)
public class EtrainsTest {
    private static final MonitoringProperties CONFIG = new MonitoringProperties();

    @Rule
    public MordaMonitoringsRule rule = new MordaMonitoringsRule();

    @Parameterized.Parameters(name = "Etrains block in {0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(Arrays.asList(
                DUBNA, VYBORG, BROVARY, ORSHA, ATBASAR
        ));
    }

    private Region region;
    private Cleanvars cleanvars;
    private Client client;

    public EtrainsTest(Region region) throws IOException {
        this.region = region;
        this.client = MordaClient.getJsonEnabledClient();

        MordaClient mordaClient = new MordaClient(CONFIG.getMordaEnv(), region.getDomain());
        mordaClient.rapidoActions(client)
                .get("etrains", new CookieHeader(new Cookie(CookieName.
                        YANDEX_GID, region.getRegionId())));

        mordaClient.tuneActions(client).setRegion(region);

        String response = mordaClient
                .rapidoActions(client)
                .getResponse("etrains", null, null, null, null)
                .readEntity(String.class);

        this.cleanvars = MordaClient.getObjectMapper().readValue(response, Cleanvars.class);
        rule.addMeta("json", response);
    }

    @Test
    public void etrainsAreShown() {
        shouldHaveParameter("Электрички отсутствуют в " + region.getName(),
                cleanvars.getEtrains(), having(on(Etrains.class).getProcessed(), equalTo(1)));

        shouldHaveParameter("Электрички отсутствуют в " + region.getName(),
                cleanvars.getEtrains(), having(on(Etrains.class).getShow(), equalTo(1)));
    }

    @Test
    public void etrainsResponse() throws IOException {
        ifEtrainsAreShown();

        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getHref(), not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getEtrains().getHref(), equalTo(HttpURLConnection.HTTP_OK));

        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getHrefBack(),
                not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getEtrains().getHrefBack(), equalTo(HttpURLConnection.HTTP_OK));

        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getRaspHost(),
                not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getEtrains().getRaspHost(), equalTo(HttpURLConnection.HTTP_OK));
        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getRaspHostBigRu(),
                not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, cleanvars.getEtrains().getRaspHostBigRu(), equalTo(HttpURLConnection.HTTP_OK));

    }

    @Test
    public void etrainsStNames() throws IOException {
        ifEtrainsAreShown();

        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getCstname(), not(isEmptyOrNullString())));
        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getStname(), not(isEmptyOrNullString())));
    }

    @Test
    public void etrainsItems() throws IOException {
        ifEtrainsAreShown();

        List<EtrainItem> allItems = new ArrayList<>();
        allItems.addAll(cleanvars.getEtrains().getFctd());
        allItems.addAll(cleanvars.getEtrains().getFctm());
        allItems.addAll(cleanvars.getEtrains().getTctd());
        allItems.addAll(cleanvars.getEtrains().getTctm());

        for (EtrainItem etrainItem : allItems) {

            shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getName(), not(isEmptyOrNullString())));
            shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getUrl(), not(isEmptyOrNullString())));
            shouldHaveResponseCode(client, etrainItem.getUrl(), equalTo(HttpURLConnection.HTTP_OK));
        }

    }

    private void ifEtrainsAreShown() {
        assumeThat("Электрички отсутствуют в " + region.getName(), cleanvars.getEtrains(),
                having(on(Etrains.class).getShow(), equalTo(1)));
    }

}
