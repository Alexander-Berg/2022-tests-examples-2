package ru.yandex.autotests.mordabackend.tabs;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.servicestabs.ServicesTab;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.TabsParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.selectFirst;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.lessThan;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assume.assumeFalse;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_TABS;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.SEARCH_REQUEST;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.getHrefMatcher;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.getUrlMatcher;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.withRequest;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.05.14
 */
@Aqua.Test(title = "Search Tabs")
@Features("Tabs")
@Stories("Search Tabs")
@RunWith(CleanvarsParametrizedRunner.class)
public class TabsTest {
    private static final Properties CONFIG = new Properties();
    public static final String SERVICES = "SERVICES";

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                    .withUserAgents(FF_34, TOUCH)
                    .withParameterProvider(new TabsParameterProvider())
                    .withCleanvarsBlocks(SERVICES_TABS);

    private final Client client;
    private final Cleanvars cleanvars;
    private final ServicesV122Entry servicesV122Entry;
    private final Region region;
    private final UserAgent userAgent;
    private ServicesTab cleanvarsEntry;

    public TabsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region, UserAgent userAgent,
                    String service, ServicesV122Entry servicesV122Entry) {
        this.client = client;
        this.region = region;
        this.cleanvars = cleanvars;
        this.userAgent = userAgent;
        this.servicesV122Entry = servicesV122Entry;
    }

    @Before
    public void setUp() {
        assumeFalse("Нет табов на новой десктопной .com.tr",
                userAgent.equals(FF_34) && region.getDomain().equals(COM_TR));
        assumeFalse("Нет таба на айфоне", userAgent.isMobile() && servicesV122Entry.getIphone() == 0);
        List<ServicesTab> allServices = new ArrayList<>();
        allServices.addAll(cleanvars.getServicesTabs().getList());
        allServices.addAll(cleanvars.getServicesTabs().getMore());
        allServices.addAll(cleanvars.getServicesTabs().getMoreLast());
        cleanvarsEntry = selectFirst(allServices, having(on(ServicesTab.class).getId(),
                equalTo(servicesV122Entry.getId())));
        assumeThat(cleanvarsEntry, notNullValue());
    }

    @Test
    public void serviceIcon() throws IOException {
        shouldHaveParameter(cleanvarsEntry, having(on(ServicesTab.class).getIcon(), equalTo(servicesV122Entry.getIcon())));
        assumeThat(cleanvarsEntry.getIcon(), not(isEmptyOrNullString()));
        String url = normalizeUrl(cleanvarsEntry.getIcon());
        shouldHaveResponseCode(client, url, equalTo(200));
    }

    @Test
    public void serviceUrl() throws IOException {
        shouldHaveParameter(cleanvarsEntry, having(on(ServicesTab.class).getUrl(),
                getUrlMatcher(servicesV122Entry, userAgent)));
        String url = normalizeUrl(cleanvarsEntry.getUrl());
        addLink(url, region, false, null, userAgent);
        shouldHaveResponseCode(client, url, lessThan(400));
    }

    @Test
    public void serviceHref() throws IOException {
        shouldHaveParameter(cleanvarsEntry, having(on(ServicesTab.class).getHref(),
                getHrefMatcher(servicesV122Entry, region, region.getDomain().getNationalLanguage(), userAgent)));
        String url = normalizeUrl(cleanvarsEntry.getHref());
        addLink(url, region, false, null, userAgent);
        shouldHaveResponseCode(client, url, lessThan(400));
    }

    @Test
    public void serviceSearch() throws IOException {
        shouldHaveParameter(cleanvarsEntry, having(on(ServicesTab.class).getSearch(),
                equalTo(servicesV122Entry.getSearch())));
        assumeThat(cleanvarsEntry.getSearch(), not(isEmptyOrNullString()));
        String url = normalizeUrl(cleanvarsEntry.getSearch());
        shouldHaveResponseCode(client, withRequest(url, SEARCH_REQUEST), lessThan(400));
    }

    @Test
    public void servicePda() throws IOException {
        assumeFalse("fotki".equals(servicesV122Entry.getId()));
        shouldHaveParameter(cleanvarsEntry, having(on(ServicesTab.class).getPda(),
                equalTo(servicesV122Entry.getPda())));
        assumeThat(cleanvarsEntry.getPda(), not(isEmptyOrNullString()));
        String url = normalizeUrl(cleanvarsEntry.getPda());
        addLink(url, region, false, null, PDA);
        shouldHaveResponseCode(client, url, PDA, lessThan(400));
    }

//    @Test
    public void serviceSearchPda() throws IOException {
        shouldHaveParameter(cleanvarsEntry, having(on(ServicesTab.class).getSearchMobile(),
                equalTo(servicesV122Entry.getSearchMobile())));
        assumeThat(cleanvarsEntry.getSearchMobile(), not(isEmptyOrNullString()));
        String url = normalizeUrl(cleanvarsEntry.getSearchMobile());
        shouldHaveResponseCode(client, withRequest(url, SEARCH_REQUEST), PDA, lessThan(400));
    }

    @Test
    public void serviceTouch() throws IOException {
        assumeThat(userAgent.getIsTouch(), equalTo(1));
        shouldHaveParameter(cleanvarsEntry, having(on(ServicesTab.class).getTouch(),
                equalTo(servicesV122Entry.getTouch())));
        assumeThat(servicesV122Entry.getTouch(), not(isEmptyOrNullString()));
        String url = normalizeUrl(cleanvarsEntry.getTouch());
        addLink(url, region, false, null, userAgent);
        shouldHaveResponseCode(client, url, userAgent, lessThan(400));
    }
}
