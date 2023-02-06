package ru.yandex.autotests.mordabackend.services;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.servicesblock.ServicesBlock;
import ru.yandex.autotests.mordabackend.beans.servicesblock.ServicesBlockLink;
import ru.yandex.autotests.mordabackend.utils.MordaVersion;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItems;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES;
import static ru.yandex.autotests.mordabackend.services.ServicesUtils.getAllDefaultBlockServices;
import static ru.yandex.autotests.mordabackend.services.ServicesUtils.getPinnedServices;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: ivannik
 * Date: 24.06.2014
 */
@Aqua.Test(title = "Services Count")
@Features("Services")
@Stories("Services Count")
@RunWith(CleanvarsParametrizedRunner.class)
public class DefaultServicesBlockCountTest {
    private static final Properties CONFIG = new Properties();
    public static final String WITH_COMMENT = "2";
    public static final String WITHOUT_COMMENT = "3";
    public static final String BLOCK_SERVICE = "4";

    @CleanvarsParametrizedRunner.Parameters("{3}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY)
                    .withCleanvarsBlocks(SERVICES);

    private Region region;
    private MordaVersion mordaVersion;
    private Cleanvars cleanvars;

    public DefaultServicesBlockCountTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region) {
        this.region = region;
        this.mordaVersion = MordaVersion.fromMordaEnv(CONFIG.getMordaEnv());
        this.cleanvars = cleanvars;
    }

    @Test
    public void defaultServices() {
        List<String> expectedServices = extract(
                getAllDefaultBlockServices(mordaVersion, region),
                on(ServicesV122Entry.class).getId());
        List<String> services = extract(
                cleanvars.getServices().getHash().get(WITH_COMMENT),
                on(ServicesBlockLink.class).getId());
        shouldMatchTo(expectedServices, hasItems(services.toArray(new String[]{})));
    }

    @Test
    public void pinnedServices() {
        List<String> expectedPinnedervices = extract(
                getPinnedServices(mordaVersion, region),
                on(ServicesV122Entry.class).getId());
        List<String> services = extract(
                cleanvars.getServices().getHash().get(WITH_COMMENT),
                on(ServicesBlockLink.class).getId());

        shouldMatchTo(services, hasItems(expectedPinnedervices.toArray(new String[]{})));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getServices(), having(on(ServicesBlock.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getServices(), having(on(ServicesBlock.class).getProcessed(), equalTo(1)));
    }
}
