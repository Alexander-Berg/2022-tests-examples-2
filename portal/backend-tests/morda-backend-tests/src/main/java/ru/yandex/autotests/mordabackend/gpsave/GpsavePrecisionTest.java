package ru.yandex.autotests.mordabackend.gpsave;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.client.ClientUtils;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParameterProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SK;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.autotests.utils.morda.url.DomainManager.getMasterDomain;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Gpsave Precision")
@Features("Gpsave")
@Stories("Gpsave Precision")
@RunWith(CleanvarsParametrizedRunner.class)
public class GpsavePrecisionTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}, {7}")
    public static ParametersUtils parameters =
            parameters(RU, BY, UA, KZ, COM_TR)
                    .withUserAgents(FF_34, PDA)
                    .withCleanvarsBlocks(SK)
                    .withParameterProvider(new ParameterProvider() {
                        @Override
                        public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars
                                cleanvars, Region region, Language language, UserAgent userAgent) {
                            List<Object[]> data = new ArrayList<>();

                            data.add(new Object[]{"55.96931716680345", "37.41953740940979", "23.12324"});
                            data.add(new Object[]{"59.79977043604069", "30.2715785887979", "42.93662"});
                            data.add(new Object[]{"55.029996228507365", "82.96912317281307", "35.32378"});

                            return data;
                        }
                    });


    private final MordaClient mordaClient;
    private final UserAgent userAgent;
    private final Region region;
    private final Client client;
    private final Cleanvars cleanvars;
    private final String lat;
    private final String lon;
    private final String precision;

    public GpsavePrecisionTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                               Region region, UserAgent userAgent, String lat, String lon, String precision) {
        this.mordaClient = mordaClient;
        this.userAgent = userAgent;
        this.region = region;
        this.client = client;
        this.cleanvars = cleanvars;
        this.lat = lat;
        this.lon = lon;
        this.precision = precision;
    }

    @Test
    public void gpsave() {
        mordaClient.gpsaveActions(client).gpsave(lat, lon, precision, cleanvars.getSk());

        String yp = ClientUtils.getCookieValue(client, "yp", ".yandex" + getMasterDomain(region.getDomain()));

        assertThat("Cookie yp not exists", yp, not(isEmptyOrNullString()));
        assertThat("Cookie yp not valid", yp, allOf(
                containsString(lat.replace('.', '_')),
                containsString(lon.replace('.', '_')),
                containsString(":" + precision.substring(0, precision.indexOf('.')) + ":")));
    }

    @Test
    public void mgpsave() {
        mordaClient.gpsaveActions(client).mgpsave(lat, lon, precision, cleanvars.getSk());

        String yp = ClientUtils.getCookieValue(client, "yp", ".yandex" + getMasterDomain(region.getDomain()));

        assertThat("Cookie yp not exists", yp, not(isEmptyOrNullString()));
        assertThat("Cookie yp not valid", yp, allOf(
                containsString(lat.replace('.', '_')),
                containsString(lon.replace('.', '_')),
                containsString(":" + precision.substring(0, precision.indexOf('.')) + ":")));
    }
}
