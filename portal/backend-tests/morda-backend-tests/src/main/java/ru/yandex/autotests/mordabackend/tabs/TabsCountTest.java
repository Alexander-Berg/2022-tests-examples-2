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
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_TABS;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.getTabsMoreServices;
import static ru.yandex.autotests.mordabackend.tabs.TabsUtils.getTabsServices;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.05.14
 */
@Aqua.Test(title = "Search Tabs Count")
@Features("Tabs")
@Stories("Search Tabs Count")
@RunWith(CleanvarsParametrizedRunner.class)
public class TabsCountTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                    .withUserAgents(FF_34, TOUCH)
                    .withCleanvarsBlocks(SERVICES_TABS);

    private final MordaClient mordaClient;
    private final Client client;
    private final Cleanvars cleanvars;
    private Region region;
    private UserAgent userAgent;

    public TabsCountTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                         UserAgent userAgent) {
        this.region = region;
        this.mordaClient = mordaClient;
        this.cleanvars = cleanvars;
        this.userAgent = userAgent;
        this.client = client;
    }

    @Before
    public void setUp() {
        assumeFalse("Нет табов на новой десктопной .com.tr",
                userAgent.equals(FF_34) && region.getDomain().equals(COM_TR));
    }

    @Test
    public void tabs() {
        List<String> expectedTabs = extract(getTabsServices(region.getDomain(), userAgent), on(ServicesV122Entry.class).getId());
        List<String> tabs = extract(cleanvars.getServicesTabs().getList(),
                on(ServicesTab.class).getId());
        assertThat(tabs, hasSameItemsAsCollection(expectedTabs));
    }

    @Test
    public void tabsMore() {
        assumeFalse("Нет табов 'ещё' на touch", userAgent.isMobile());
        List<String> expectedTabs = extract(getTabsMoreServices(region.getDomain()), on(ServicesV122Entry.class).getId());
        List<String> services = extract(cleanvars.getServicesTabs().getMore(), on(ServicesTab.class).getId());
        services.addAll(extract(cleanvars.getServicesTabs().getMoreLast(), on(ServicesTab.class).getId()));
        assertThat(services, hasSameItemsAsCollection(expectedTabs));
    }
}
