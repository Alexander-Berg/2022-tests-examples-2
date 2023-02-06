package ru.yandex.autotests.mordabackend.mobile.services;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.servicesmobile.ServiceMobileItem;
import ru.yandex.autotests.mordabackend.beans.servicesmobile.ServicesMobile;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_MOBILE;
import static ru.yandex.autotests.mordabackend.mobile.services.ServicesMobileUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.mobile.services.ServicesMobileUtils.SERVICES_MOBILE_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.mobile.services.ServicesMobileUtils.USER_AGENTS;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.attach;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.parameters.ServicesParameterProvider.getTouchServices;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 22.08.2014
 */
@Aqua.Test(title = "Mobile Services")
@Features("Mobile")
@Stories("Mobile Services")
@RunWith(CleanvarsParametrizedRunner.class)
public class ServicesMobileTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(SERVICES_MOBILE_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(USER_AGENTS)
                    .withCleanvarsBlocks(SERVICES_MOBILE);


    private Cleanvars cleanvars;
    private Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;

    public ServicesMobileTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                              Language language, UserAgent userAgent) {
        this.cleanvars = cleanvars;
        this.client = client;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        attach(cleanvars.getServicesMobile());
    }

    @Test
    public void servicesMobileList() {
        List<String> expectedItems = extract(getTouchServices(region, language, userAgent),
                on(ServicesV122Entry.class).getId());
        List<ServiceMobileItem> actualServices = new ArrayList<>();
        actualServices.addAll(cleanvars.getServicesMobile().getList());
        actualServices.addAll(cleanvars.getServicesMobile().getListMore());
        List<String> actualItems = extract(actualServices, on(ServiceMobileItem.class).getId());

        shouldHaveParameter(actualItems, hasSameItemsAsCollection(expectedItems));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getServicesMobile(), having(on(ServicesMobile.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getServicesMobile(), having(on(ServicesMobile.class).getProcessed(), equalTo(1)));
    }
}
