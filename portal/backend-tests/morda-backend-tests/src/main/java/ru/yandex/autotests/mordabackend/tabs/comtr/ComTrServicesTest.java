package ru.yandex.autotests.mordabackend.tabs.comtr;

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
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesTabsParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesTabsEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.selectFirst;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_TABS;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.SEARCH_REQUEST;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.getComTrUrl;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.withRequest;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: ivannik
 * Date: 11.09.2014
 */
@Aqua.Test(title = "Comtr Services Items")
@Features("Comtr Services")
@Stories("Comtr Services Items")
@RunWith(CleanvarsParametrizedRunner.class)
public class ComTrServicesTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(COM_TR)
                    .withUserAgents(FF_34)
                    .withParameterProvider(new ServicesTabsParameterProvider("comtr"))
                    .withCleanvarsBlocks(SERVICES_TABS);

    private final Client client;
    private final Cleanvars cleanvars;
    private Region region;
    private UserAgent userAgent;
    private ServicesTabsEntry servicesTabsEntry;
    private ServicesTab cleanvarsEntry;

    public ComTrServicesTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                  UserAgent userAgent, String serviceId, ServicesTabsEntry servicesTabsEntry) {
        this.region = region;
        this.cleanvars = cleanvars;
        this.servicesTabsEntry = servicesTabsEntry;
        this.client = client;
        this.userAgent = userAgent;
    }

    @Before
    public void setUp() {
        cleanvarsEntry = selectFirst(cleanvars.getServicesTabs().getList(), allOf(
                having(on(ServicesTab.class).getId(), equalTo(servicesTabsEntry.getId())),
                having(on(ServicesTab.class).getContent(), equalTo(servicesTabsEntry.getContent()))));
        assertThat("Не найден сервис с id " + servicesTabsEntry.getId(), cleanvarsEntry, notNullValue());
    }

    @Test
    public void servicesExportValues() {
        shouldMatchTo(cleanvarsEntry, allOf(
                having(on(ServicesTab.class).getDomain(), equalTo(servicesTabsEntry.getDomain())),
                having(on(ServicesTab.class).getContent(), equalTo(servicesTabsEntry.getContent())),
                having(on(ServicesTab.class).getId(), equalTo(servicesTabsEntry.getId())),
                having(on(ServicesTab.class).getTabs(), equalTo(servicesTabsEntry.getTabs()))
        ));
    }

    @Test
    public void servicesUrl() throws IOException {
        shouldHaveParameter(cleanvarsEntry,
                having(on(ServicesTab.class).getUrl(), equalTo(getComTrUrl(servicesTabsEntry))));
        shouldHaveResponseCode(client, normalizeUrl(cleanvarsEntry.getUrl()), userAgent, equalTo(200));
    }

    @Test
    public void servicesFamilyUrl() throws IOException {
        shouldHaveParameter(cleanvarsEntry,
                having(on(ServicesTab.class).getUrlFamily(), equalTo(servicesTabsEntry.getUrlFamily())));
        assumeThat(cleanvarsEntry.getUrlFamily(), not(isEmptyOrNullString()));
        shouldHaveResponseCode(client, normalizeUrl(cleanvarsEntry.getUrlFamily()), userAgent, equalTo(200));
    }

    @Test
    public void servicesSearch() throws IOException {
        shouldHaveParameter(cleanvarsEntry,
                having(on(ServicesTab.class).getSearch(), equalTo(servicesTabsEntry.getSearch())));
        assumeThat(cleanvarsEntry.getSearch(), not(isEmptyOrNullString()));
        shouldHaveResponseCode(client,
                withRequest(normalizeUrl(cleanvarsEntry.getSearch()), SEARCH_REQUEST), userAgent, equalTo(200));
    }

    @Test
    public void servicesSearchFamily() throws IOException {
        shouldHaveParameter(cleanvarsEntry,
                having(on(ServicesTab.class).getSearchFamily(), equalTo(servicesTabsEntry.getSearchFamily())));
        assumeThat(cleanvarsEntry.getSearchFamily(), not(isEmptyOrNullString()));
        shouldHaveResponseCode(client,
                withRequest(normalizeUrl(cleanvarsEntry.getSearchFamily()), SEARCH_REQUEST), userAgent, equalTo(200));
    }

    @Test
    public void servicesIconPng() throws IOException {
        shouldHaveParameter(cleanvarsEntry,
                having(on(ServicesTab.class).getIconPng(), equalTo(servicesTabsEntry.getIconPng())));
        shouldHaveResponseCode(client, normalizeUrl(cleanvarsEntry.getIconPng()), userAgent, equalTo(200));
    }

    @Test
    public void servicesIconSvg() throws IOException {
        shouldHaveParameter(cleanvarsEntry,
                having(on(ServicesTab.class).getIconSvg(), equalTo(servicesTabsEntry.getIconSvg())));
        shouldHaveResponseCode(client, normalizeUrl(cleanvarsEntry.getIconSvg()), userAgent, equalTo(200));
    }
}
