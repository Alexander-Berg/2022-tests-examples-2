package ru.yandex.autotests.mordabackend.firefox.tabs;

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
import ru.yandex.autotests.utils.morda.BaseProperties.MordaEnv;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_TABS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.utils.morda.url.Domain.*;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.05.14
 */
@Aqua.Test(title = "Firefox Search Tabs Count")
@Features("Firefox")
@Stories("Firefox Search Tabs Count")
@RunWith(CleanvarsParametrizedRunner.class)
public class FirefoxTabsCountTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(new MordaEnv(CONFIG.getMordaEnv().getEnv().replace("www-", "firefox-")),
                    RU, UA, COM_TR)
                    .withLanguages(Language.RU, Language.UK, Language.BE, Language.KK, Language.TT)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(SERVICES_TABS);

    private final Cleanvars cleanvars;
    private Region region;

    public FirefoxTabsCountTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                Language language, UserAgent userAgent) {
        this.region = region;
        this.cleanvars = cleanvars;
    }

    @Test
    public void tabs() {
        List<String> expectedTabs = extract(exports(MordaExports.SERVICES_TABS,
                        domain(region.getDomain()),
                        having(on(ServicesTabsEntry.class).getContent(), equalTo("firefox")),
                        having(on(ServicesTabsEntry.class).getTabs(), not(isEmptyOrNullString()))),
                on(ServicesTabsEntry.class).getId());
        List<String> tabs = extract(cleanvars.getServicesTabs().getList(),
                on(ServicesTab.class).getId());
        assertThat(tabs, hasSameItemsAsCollection(expectedTabs));
    }
}
