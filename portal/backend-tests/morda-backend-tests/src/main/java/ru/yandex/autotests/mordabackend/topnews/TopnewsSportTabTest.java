package ru.yandex.autotests.mordabackend.topnews;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTab;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesV122ParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.TOPNEWS;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.NEWS;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.SPORT;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.TOPNEWS_REGIONS_MAIN;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.getSportHrefMatcher;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.shouldSeeNewsSportTab;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;

/**
 * User: eoff
 * Date: 20.06.2014
 */
@Aqua.Test(title = "Sport Tab")
@Features("Topnews")
@Stories("Sport Tab")
@RunWith(CleanvarsParametrizedRunner.class)
public class TopnewsSportTabTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(TOPNEWS_REGIONS_MAIN)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withParameterProvider(new ServicesV122ParameterProvider(NEWS))
                    .withCleanvarsBlocks(TOPNEWS);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final Language language;
    private final UserAgent userAgent;
    private final ServicesV122Entry servicesV12Entry;
    private TopnewsTab tab;

    public TopnewsSportTabTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                               Language language, UserAgent userAgent, ServicesV122Entry servicesV12Entry) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.servicesV12Entry = servicesV12Entry;
    }

    @Before
    public void setUp() {
        assumeTrue("Таба sport нет", cleanvars.getTopnews().getTabshash().containsKey(SPORT));
        tab = cleanvars.getTopnews().getTabshash().get(SPORT);
    }

    @Test
    public void sportHref() throws IOException {
        shouldHaveParameter(tab, having(on(TopnewsTab.class).getHref(),
                getSportHrefMatcher(servicesV12Entry, userAgent, language)));
        addLink(tab.getHref(), region, false, language, userAgent);
        shouldHaveResponseCode(client, normalizeUrl(tab.getHref()), equalTo(200));
    }

    @Test
    public void sportTabParameters() {
        shouldSeeNewsSportTab(tab, region, userAgent);
    }
}
