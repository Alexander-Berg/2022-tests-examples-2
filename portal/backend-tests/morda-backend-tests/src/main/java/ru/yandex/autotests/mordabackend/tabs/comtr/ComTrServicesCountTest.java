package ru.yandex.autotests.mordabackend.tabs.comtr;

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
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesTabsEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_TABS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 11.09.2014
 */
@Aqua.Test(title = "Comtr Services Count")
@Features("Comtr Services")
@Stories("Comtr Services Count")
@RunWith(CleanvarsParametrizedRunner.class)
public class ComTrServicesCountTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(COM_TR)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(SERVICES_TABS);

    private final Cleanvars cleanvars;
    private Region region;

    public ComTrServicesCountTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                         UserAgent userAgent) {
        this.region = region;
        this.cleanvars = cleanvars;
    }

    @Test
    public void services() {
        List<String> expectedTabs =
                extract(exports(MordaExports.SERVICES_TABS, domain(region.getDomain()),
                                having(on(ServicesTabsEntry.class).getContent(),
                                        equalTo(region.getDomain().toString().replaceAll("\\.", "")))),
                        on(ServicesTabsEntry.class).getId());
        List<String> tabs = extract(cleanvars.getServicesTabs().getList(),
                on(ServicesTab.class).getId());
        assertThat(tabs, hasSameItemsAsCollection(expectedTabs));
    }
}
