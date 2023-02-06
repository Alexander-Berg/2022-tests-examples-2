package ru.yandex.autotests.mordabackend.mobile.metro;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.metro.Metro;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.MetroTouchEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEOID;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGE_LC;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.METRO;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MORDA_ZONE;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.METRO_TOUCH;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Metro Block")
@Features("Mobile")
@Stories("Metro Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class MetroTouchBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK)
                    .withUserAgents(TOUCH, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(METRO, GEOID, MORDA_ZONE, LANGUAGE_LC);

    private final Cleanvars cleanvars;
    private final Client client;
    private final UserAgent userAgent;

    private MetroTouchEntry metroTouchEntry;

    public MetroTouchBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                     UserAgent userAgent) {
        this.cleanvars = cleanvars;
        this.client = client;
        this.userAgent = userAgent;
    }

    @Before
    public void init() {
        metroTouchEntry = export(METRO_TOUCH,
                domain(cleanvars.getMordaZone()), lang(cleanvars.getLanguageLc()), geo(cleanvars.getGeoID()));
        assertThat("Нет соответствующего экспорта metro_touch", metroTouchEntry, notNullValue());
    }

    @Test
    public void metro() throws IOException {
        shouldMatchTo(cleanvars.getMetro(), allOfDetailed(
                hasPropertyWithValue(on(Metro.class).getProcessed(), equalTo(1)),
                hasPropertyWithValue(on(Metro.class).getShow(), equalTo(1)),
                hasPropertyWithValue(on(Metro.class).getDomain(), equalTo(metroTouchEntry.getDomain())),
                hasPropertyWithValue(on(Metro.class).getLang(), equalTo(metroTouchEntry.getLang())),
                hasPropertyWithValue(on(Metro.class).getGeo(), equalTo(metroTouchEntry.getGeo())),
                hasPropertyWithValue(on(Metro.class).getIcon(), equalTo(metroTouchEntry.getIcon())),
                hasPropertyWithValue(on(Metro.class).getCounter(), equalTo(metroTouchEntry.getCounter())),
                hasPropertyWithValue(on(Metro.class).getUrl(), equalTo(metroTouchEntry.getUrl()))
        ));
        shouldHaveResponseCode(client, normalizeUrl(cleanvars.getMetro().getUrl()), userAgent, equalTo(200));
    }
}
