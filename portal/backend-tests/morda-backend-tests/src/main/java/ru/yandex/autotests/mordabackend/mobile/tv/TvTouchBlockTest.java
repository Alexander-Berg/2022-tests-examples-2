package ru.yandex.autotests.mordabackend.mobile.tv;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.tv.Tv;
import ru.yandex.autotests.mordabackend.beans.tv.TvAnnounce;
import ru.yandex.autotests.mordabackend.beans.tv.TvEvent;
import ru.yandex.autotests.mordabackend.beans.tv.TvTab;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordaexportsclient.beans.TvAnnouncesEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEOID;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.ISHOLIDAY;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LANGUAGE_LC;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LOCAL;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MORDA_CONTENT;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.TV;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.YYYYMMDD;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.TV_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvChHrefMatcher;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvEventHrefMatcher;
import static ru.yandex.autotests.mordabackend.tv.TvUtils.getTvHrefMatcher;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.TV_ANNOUNCES;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeosMatcher.geos;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Mobile Tv Block")
@Features("Mobile")
@Stories("Mobile Tv Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class TvTouchBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(TV_REGIONS_ALL)
                    .withUserAgents(TOUCH, WP8, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(TV, LOCAL, ISHOLIDAY, MORDA_CONTENT, YYYYMMDD, GEOID, LANGUAGE_LC);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final UserAgent userAgent;

    private ServicesV122Entry servicesV122Entry;
    private List<TvAnnouncesEntry> tvAnnouncesEntries;

    public TvTouchBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                            UserAgent userAgent) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.userAgent = userAgent;
    }

    @Before
    public void init() {
        servicesV122Entry = export(SERVICES_V12_2, domain(region.getDomain()),
                having(on(ServicesV122Entry.class).getId(), equalTo("tv")));

        tvAnnouncesEntries = exports(TV_ANNOUNCES,
                having(on(TvAnnouncesEntry.class).getFrom(), before(cleanvars.getYYYYMMDD())),
                having(on(TvAnnouncesEntry.class).getTo(), after(cleanvars.getYYYYMMDD())),
                geos(cleanvars.getGeoID()),
                having(on(TvAnnouncesEntry.class).getContent(), equalTo(cleanvars.getMordaContent())));
    }

    @Test
    public void tv() throws IOException {
        shouldMatchTo(cleanvars.getTV(), allOfDetailed(
                hasPropertyWithValue(on(Tv.class).getProcessed(), equalTo(1)),
                hasPropertyWithValue(on(Tv.class).getShow(), equalTo(1)),
                hasPropertyWithValue(on(Tv.class).getHref(),
                        getTvHrefMatcher(servicesV122Entry, region, userAgent))
        ));
        shouldHaveResponseCode(client, normalizeUrl(cleanvars.getTV().getHref()), equalTo(200));

    }

    @Test
    public void announces() throws IOException {
        for (TvAnnounce announce : cleanvars.getTV().getAnnounces()) {
            Matcher<? super TvAnnouncesEntry> entryMatcher = allOfDetailed(
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getFilter(), equalTo(announce.getFilter())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getContent(), equalTo(announce.getContent())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getId(), equalTo(announce.getId())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getDomain(), equalTo(announce.getDomain())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getFrom(), equalTo(announce.getFrom())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getTo(), equalTo(announce.getTo())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getLang(), equalTo(announce.getLang())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getGeos(), equalTo(announce.getGeos())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getTanker(), equalTo(announce.getTanker())),
                    hasPropertyWithValue(on(TvAnnouncesEntry.class).getUrl(), equalTo(announce.getUrl()))
            );
            shouldMatchTo(tvAnnouncesEntries, hasItem(entryMatcher));
            shouldHaveResponseCode(client, normalizeUrl(announce.getUrl()), equalTo(200));
        }
        shouldMatchTo(cleanvars.getTV().getAnnounces(), hasSize(Math.min(1, tvAnnouncesEntries.size())));

    }

    @Test
    public void nowTabs() throws IOException {
        shouldMatchTo(cleanvars.getTV().getTabs(), hasSize(greaterThan(0)));
        List<TvTab> tvTabs = select(cleanvars.getTV().getTabs(), having(on(TvTab.class).getType(), equalTo("now")));
        shouldMatchTo(tvTabs, hasSize(1));
        for (TvTab tvTab : tvTabs) {
            shouldMatchTo(tvTab, allOfDetailed(
                    hasPropertyWithValue(on(TvTab.class).getChannel(), equalTo(0)),
                    hasPropertyWithValue(on(TvTab.class).getChannelId(), isEmptyOrNullString()),
                    hasPropertyWithValue(on(TvTab.class).getChname(), isEmptyOrNullString()),
                    hasPropertyWithValue(on(TvTab.class).getType(), equalTo("now")),
                    hasPropertyWithValue(on(TvTab.class).getHref(),
                            getTvHrefMatcher(servicesV122Entry, region, userAgent))
            ));
            checkProgramms(tvTab.getProgramms());
            shouldHaveResponseCode(client, normalizeUrl(tvTab.getHref()), equalTo(200));
        }

    }

    @Test
    public void channelTabs() throws IOException {
        shouldMatchTo(cleanvars.getTV().getTabs(), hasSize(greaterThan(0)));
        List<TvTab> tvTabs = select(cleanvars.getTV().getTabs(), having(on(TvTab.class).getType(), equalTo("channel")));
        shouldMatchTo(tvTabs, hasSize(greaterThan(0)));
        for (TvTab tvTab : tvTabs) {
            shouldMatchTo(tvTab, allOfDetailed(
                    hasPropertyWithValue(on(TvTab.class).getChannel(), equalTo(1)),
                    hasPropertyWithValue(on(TvTab.class).getChannelId(), not(isEmptyOrNullString())),
                    hasPropertyWithValue(on(TvTab.class).getChname(), not(isEmptyOrNullString())),
                    hasPropertyWithValue(on(TvTab.class).getType(), equalTo("channel")),
                    hasPropertyWithValue(on(TvTab.class).getHref(), getTvChHrefMatcher(cleanvars, tvTab.getChannelId()))
            ));
            checkProgramms(tvTab.getProgramms());
            shouldHaveResponseCode(client, normalizeUrl(tvTab.getHref()), equalTo(200));
        }

    }

    private void checkProgramms(List<TvEvent> programms) throws IOException {
        List<TvEvent> events = select(programms, having(on(TvEvent.class).getType(), not("separator")));
        for (TvEvent event : events.subList(0, Math.min(2, events.size()))) {
            shouldMatchTo(event, allOfDetailed(
                    hasPropertyWithValue(on(TvEvent.class).getHref(), getTvEventHrefMatcher(cleanvars)),
                    hasPropertyWithValue(on(TvEvent.class).getChHref(), getTvChHrefMatcher(cleanvars, event.getChId())),
                    hasPropertyWithValue(on(TvEvent.class).getChannel(), not(isEmptyOrNullString())),
                    hasPropertyWithValue(on(TvEvent.class).getName(), not(isEmptyOrNullString())),
                    hasPropertyWithValue(on(TvEvent.class).getFull(), not(isEmptyOrNullString()))
            ));
            shouldHaveResponseCode(client, normalizeUrl(event.getHref()), userAgent, equalTo(200));
            shouldHaveResponseCode(client, normalizeUrl(event.getChHref()), userAgent, equalTo(200));
        }
    }
}
