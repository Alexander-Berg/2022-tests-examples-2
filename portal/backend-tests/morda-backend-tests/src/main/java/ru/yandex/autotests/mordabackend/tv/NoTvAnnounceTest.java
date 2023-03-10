package ru.yandex.autotests.mordabackend.tv;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.tv.Tv;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.CleanvarsUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesV122ParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordaexportsclient.beans.TvAnnouncesEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.text.ParseException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HIDDENTIME;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.TV;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.TV_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvAnnounce;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: eoff
 * Date: 20.06.2014
 */
@Aqua.Test(title = "No Announces")
@Features("Tv")
@Stories("No Announces")
@RunWith(CleanvarsParametrizedRunner.class)
public class NoTvAnnounceTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(TV_REGIONS_ALL)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withParameterProvider(new ServicesV122ParameterProvider("tv"))
                    .withCleanvarsBlocks(TV, HIDDENTIME);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final UserAgent userAgent;
    private final ServicesV122Entry servicesV122Entry;
    private TvAnnouncesEntry tvAnnouncesEntry;

    public NoTvAnnounceTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                            UserAgent userAgent, ServicesV122Entry servicesV122Entry) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.userAgent = userAgent;
        this.servicesV122Entry = servicesV122Entry;
    }

    @Before
    public void getAnnounce() throws ParseException {
        this.tvAnnouncesEntry = getTvAnnounce(cleanvars.getHiddenTime(), region, userAgent);
        assumeTrue("?????????????????? ???????????? ???????? ?????? ????????????", tvAnnouncesEntry == null);
    }

    @Test
    public void noAnnounce() {
        CleanvarsUtils.shouldHaveParameter(cleanvars.getTV(), having(on(Tv.class).getAnnounces(), hasSize(0)));
    }
}
