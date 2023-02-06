package ru.yandex.autotests.mordabackend.mobile.services;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.servicesmobile.ServiceMobileItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES_MOBILE;
import static ru.yandex.autotests.mordabackend.mobile.services.ServicesMobileUtils.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.*;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.parameters.ServicesParameterProvider.Morda.TOUCH;

/**
 * User: ivannik
 * Date: 22.08.2014
 */
@Aqua.Test(title = "Mobile Services Items")
@Features("Mobile")
@Stories("Mobile Services Items")
@RunWith(CleanvarsParametrizedRunner.class)
public class ServicesMobileItemsTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(SERVICES_MOBILE_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(USER_AGENTS)
                    .withParameterProvider(new ServicesParameterProvider(TOUCH))
                    .withCleanvarsBlocks(SERVICES_MOBILE);


    private Cleanvars cleanvars;
    private Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private ServicesV122Entry expectedEntry;
    private ServiceMobileItem actualEntry;

    public ServicesMobileItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                   Language language, UserAgent userAgent, String serviceId,
                                   ServicesV122Entry servicesV122Entry) {
        this.cleanvars = cleanvars;
        this.client = client;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.expectedEntry = servicesV122Entry;
    }

    @Before
    public void setUp() {
        List<ServiceMobileItem> actualServices = new ArrayList<>();
        actualServices.addAll(cleanvars.getServicesMobile().getList());
        actualServices.addAll(cleanvars.getServicesMobile().getListMore());
        actualEntry = selectFirst(actualServices, having(on(ServiceMobileItem.class).getId(),
                equalTo(expectedEntry.getId())));
        shouldMatchTo(actualEntry, notNullValue());
        attach(actualEntry);
    }

    @Test
    public void serviceItems() throws IOException {
        shouldMatchTo(actualEntry, allOfDetailed(
                hasPropertyWithValue(on(ServiceMobileItem.class).getAllBig(), equalTo(expectedEntry.getAllBig())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getAllGroup(), equalTo(expectedEntry.getAllGroup())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getAllMobile(), equalTo(expectedEntry.getAllMobile())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getAndroid(), equalTo(expectedEntry.getAndroid())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getBada(), equalTo(expectedEntry.getBada())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getDisabled(), equalTo(expectedEntry.getDisabled())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getDomain(), equalTo(expectedEntry.getDomain())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getHref(), getHrefMatcher(expectedEntry)),
                hasPropertyWithValue(on(ServiceMobileItem.class).getIcon(), equalTo(expectedEntry.getIcon())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getIphone(), equalTo(expectedEntry.getIphone())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getMobMorda(), equalTo(expectedEntry.getMobMorda())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getMorda(), equalTo(expectedEntry.getMorda())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getMordaWeight(),
                        equalTo(expectedEntry.getMordaWeight())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getPanel(), equalTo(expectedEntry.getPanel())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getPda(), equalTo(expectedEntry.getPda())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getSearch(), getSearchUrlMatcher(expectedEntry)),
                hasPropertyWithValue(on(ServiceMobileItem.class).getSearchMobile(),
                        equalTo(expectedEntry.getSearchMobile())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getTabs(), equalTo(expectedEntry.getTabs())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getTabsMore(), equalTo(expectedEntry.getTabsMore())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getTabsTouch(), equalTo(expectedEntry.getTabsTouch())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getTouch(), equalTo(expectedEntry.getTouch())),
                hasPropertyWithValue(on(ServiceMobileItem.class).getUrl(), getUrlMatcher(expectedEntry)),
                hasPropertyWithValue(on(ServiceMobileItem.class).getWp(), equalTo(expectedEntry.getWp()))
        ));
        if(!"translate".equals(expectedEntry.getId()) && !"realty".equals(expectedEntry.getId())){
            addLink(actualEntry.getPda(), region, false, language, userAgent);
        }
        shouldHaveResponseCode(client, actualEntry.getHref(), equalTo(200));
    }
}
