package ru.yandex.autotests.mordabackend.tv;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.tv.Tv;
import ru.yandex.autotests.mordabackend.beans.tv.TvEvent;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesV122ParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.ISHOLIDAY;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LOCAL;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.TV;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvChHrefMatcher;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvEventHrefMatcher;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvEventsNumber;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvHrefMatcher;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.shouldSeeTvEventTitle;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: eoff
 * Date: 20.06.2014
 */
@Aqua.Test(title = "Tv Block")
@Features("Tv")
@Stories("Tv Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class TvBlockTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(Region.MOSCOW)//TV_REGIONS_ALL)
                    .withUserAgents(FF_34, PDA)
                    .withParameterProvider(new ServicesV122ParameterProvider("tv"))
                    .withCleanvarsBlocks(TV, LOCAL, ISHOLIDAY);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final UserAgent userAgent;
    private final ServicesV122Entry servicesV122Entry;

    public TvBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                       UserAgent userAgent, ServicesV122Entry servicesV122Entry) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.userAgent = userAgent;
        this.servicesV122Entry = servicesV122Entry;
    }

    @Before
    public void tvPresent()  {
        assumeFalse("В турции на PDA нет тв",
                userAgent.equals(UserAgent.PDA) && region.getDomain().equals(Domain.COM_TR));
    }

    @Test
    public void tvHref() throws IOException {
        shouldHaveParameter(cleanvars.getTV(),
                having(on(Tv.class).getHref(), getTvHrefMatcher(servicesV122Entry, region, userAgent)));
        addLink(cleanvars.getTV().getHref(), region, false, null, userAgent);
        shouldHaveResponseCode(client, normalizeUrl(cleanvars.getTV().getHref()), userAgent, equalTo(200));
    }

    @Test
    public void countTvEvents() throws IOException {
        shouldHaveParameter(cleanvars.getTV(),
                having(on(Tv.class).getProgramms(), hasSize(allOf(
                        greaterThan(0),
                        lessThanOrEqualTo(getTvEventsNumber(cleanvars.getTV()))))));
    }

    @Test
    public void showFlag() throws IOException {
        shouldHaveParameter(cleanvars.getTV(),
                having(on(Tv.class).getShow(), equalTo(1)));
    }

    @Test
    public void tvEventHref() throws IOException {
        for (TvEvent event : cleanvars.getTV().getProgramms()) {
            Matcher<String> tvEventHrefMatcher = getTvEventHrefMatcher(cleanvars);
            shouldHaveParameter(event, having(on(TvEvent.class).getHref(), tvEventHrefMatcher));
            shouldHaveResponseCode(client, normalizeUrl(event.getHref()), userAgent, equalTo(200));
        }
    }

    @Test
    public void tvEventChHref() throws IOException {
        for (TvEvent event : cleanvars.getTV().getProgramms()) {
            shouldHaveParameter(event, having(on(TvEvent.class).getChHref(),
                    getTvChHrefMatcher(cleanvars, event.getChId())));
            shouldHaveResponseCode(client, normalizeUrl(event.getChHref()), userAgent, equalTo(200));
        }
    }

    @Test
    public void tvEventChannel() throws IOException {
        for (TvEvent event : cleanvars.getTV().getProgramms()) {
            shouldHaveParameter(event, having(on(TvEvent.class).getChannel(), not(isEmptyOrNullString())));
        }
    }

    @Test
    public void tvEventName() throws IOException {
        for (TvEvent event : cleanvars.getTV().getProgramms()) {
            shouldHaveParameter(event, having(on(TvEvent.class).getName(), not(isEmptyOrNullString())));
            shouldHaveParameter(event, having(on(TvEvent.class).getFull(), not(isEmptyOrNullString())));
            shouldSeeTvEventTitle(event);
        }
    }
}
