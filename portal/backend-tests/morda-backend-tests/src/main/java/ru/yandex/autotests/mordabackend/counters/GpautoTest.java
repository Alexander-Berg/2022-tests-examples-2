package ru.yandex.autotests.mordabackend.counters;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.cookie.YpCookieUtils;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.Collections;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.REQUESTID;
import static ru.yandex.autotests.mordabackend.counters.GpautoUtils.getExpNode;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Gpauto")
@Features("Counters")
@Stories("Gpauto")
@RunWith(CleanvarsParametrizedRunner.class)
public class GpautoTest {
    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                    .withUserAgents(FF_34, PDA, TOUCH, ANDROID_HTC_SENS, WP8)
                    .withCleanvarsBlocks(REQUESTID)
                    .withCounters();


    private final MordaClient mordaClient;
    private final UserAgent userAgent;
    private final Region region;
    private final Client client;
    private final Cleanvars cleanvars;

    public GpautoTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                        Region region, UserAgent userAgent) {
        this.mordaClient = mordaClient;
        this.userAgent = userAgent;
        this.region = region;
        this.client = client;
        this.cleanvars = cleanvars;
    }

    @Test
    public void gpautoNo() {
        JsonNode gpautoNo =
                getExpNode(mordaClient.logsActions(client).getBlockDisplay(cleanvars.getRequestid()), "gpauto_no");
        assertThat("gpauto_no not exists", gpautoNo.isMissingNode(), equalTo(false));
        assertThat("gpauto_no not valid", gpautoNo.asText(), equalTo("1"));
    }

    @Test
    public void gpautoNew() {
        String gpautoCookie =
                GpautoUtils.getGpautoWithCoords("59_8407475", "30_30942", "124", System.currentTimeMillis() / 1000);
        YpCookieUtils.addToYpCookie(client, region, gpautoCookie);
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client)
                .getWithCounters(userAgent, Collections.singletonList(REQUESTID));

        JsonNode gpautoNo =
                getExpNode(mordaClient.logsActions(client).getBlockDisplay(cleanvars.getRequestid()), "gpauto_new");

        assertThat("gpauto_new not exists", gpautoNo.isMissingNode(), equalTo(false));
        assertThat("gpauto_new not valid", gpautoNo.asText(), equalTo("1"));
    }

    @Test
    public void gpautoOld() {
        String gpautoCookie =
                GpautoUtils.getGpautoWithCoords("59_8407475", "30_30942", "124",
                        (System.currentTimeMillis() / 1000 - 1200));
        YpCookieUtils.addToYpCookie(client, region, gpautoCookie);
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client)
                .getWithCounters(userAgent, Collections.singletonList(REQUESTID));

        JsonNode gpautoNo =
                getExpNode(mordaClient.logsActions(client).getBlockDisplay(cleanvars.getRequestid()), "gpauto_old");

        assertThat("gpauto_old not exists", gpautoNo.isMissingNode(), equalTo(false));
        assertThat("gpauto_old not valid", gpautoNo.asText(), equalTo("1"));
    }
}
