package ru.yandex.autotests.mordabackend.firefox.tabs;

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
import ru.yandex.autotests.utils.morda.BaseProperties.MordaEnv;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_TABS;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.05.14
 */
@Aqua.Test(title = "Firefox Search Tabs")
@Features("Firefox")
@Stories("Firefox Search Tabs")
@RunWith(CleanvarsParametrizedRunner.class)
public class FirefoxTabsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(new MordaEnv(CONFIG.getMordaEnv().getEnv().replace("www-", "firefox-")),
                    RU, UA, COM_TR)
                    .withLanguages(Language.RU, Language.UK, Language.BE, Language.KK, Language.TT)
                    .withUserAgents(FF_34)
                    .withParameterProvider(new ServicesTabsParameterProvider("firefox"))
                    .withCleanvarsBlocks(SERVICES_TABS);

    private final Client client;
    private final Cleanvars cleanvars;
    private UserAgent userAgent;
    private ServicesTabsEntry servicesTabsEntry;
    private ServicesTab cleanvarsEntry;

    public FirefoxTabsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                           Language language, UserAgent userAgent, String serviceId,
                           ServicesTabsEntry servicesTabsEntry)
    {
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
    public void servicesSearch() throws IOException {
        shouldHaveParameter(cleanvarsEntry,
                having(on(ServicesTab.class).getSearch(), equalTo(servicesTabsEntry.getSearch())));
        shouldHaveResponseCode(client,
                withRequest(normalizeUrl(cleanvarsEntry.getSearch()), SEARCH_REQUEST), userAgent, equalTo(200));
    }
}
