package ru.yandex.autotests.mordabackend.geo;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.geo.GeoItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.GeoParametrProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.GeoEntry;
import ru.yandex.autotests.mordaexportsclient.beans.GeoServicesV14Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEO;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 10.07.2014
 */
@Aqua.Test(title = "Geo Block Items")
@Features("Geo")
@Stories("Geo Block Items")
@RunWith(CleanvarsParametrizedRunner.class)
public class GeoItemsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(GEO_REGIONS_MAIN)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34)
                    .withParameterProvider(new GeoParametrProvider(TRAFFIC, METRO, PANORAMS, ROUTES, TAXI))
                    .withCleanvarsBlocks(GEO);

    private Client client;
    private Region region;
    private UserAgent userAgent;
    private GeoItem geoItem;
    private GeoServicesV14Entry geoServiceExport;
    private GeoEntry geoExport;

    public GeoItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                        Language language, UserAgent userAgent, String itemId, GeoItem geoItem) {
        this.client = client;
        this.region = region;
        this.userAgent = userAgent;
        this.geoItem = geoItem;
        this.geoServiceExport = getGeoService(itemId, region.getDomain(), language, region);
        this.geoExport = getGeoEntry(itemId, geoServiceExport, region.getDomain(), language, region);
    }

    @Before
    public void preCheck() {
        assertThat("Нет соответствующего экспорта geo для: " + geoItem, geoExport, notNullValue());
    }

    @Test
    public void itemDomain() {
        shouldHaveParameter(geoItem, having(on(GeoItem.class).getDomain(), equalTo(geoExport.getDomain())));
    }

    @Test
    public void itemGeo() {
        shouldHaveParameter(geoItem, having(on(GeoItem.class).getGeo(), equalTo(geoExport.getGeo())));
    }

    @Test
    public void itemLanguage() {
        shouldHaveParameter(geoItem, having(on(GeoItem.class).getLang(), equalTo(geoExport.getLang())));
    }

    @Test
    public void serviceName() {
        shouldHaveParameter(geoItem, having(on(GeoItem.class).getService(),
                equalTo(geoServiceExport.getService())));
    }

//    @Test
    public void serviceIcon() {
        if (NO_ICONS_REGIONS.contains(region)) {
            shouldHaveParameter(geoItem,
                    having(on(GeoItem.class).getServiceIcon(), equalTo(0)));
        } else {
            shouldHaveParameter(geoItem,
                    having(on(GeoItem.class).getServiceIcon(), equalTo(geoServiceExport.getServiceIcon())));
        }
    }

    @Test
    public void serviceLink() {
        shouldHaveParameter(geoItem,
                having(on(GeoItem.class).getServiceLink(), equalTo(geoServiceExport.getServiceLink())));
    }

    @Test
    public void serviceWeight() {
        shouldHaveParameter(geoItem,
                having(on(GeoItem.class).getServiceWeight(), equalTo(geoServiceExport.getServiceWeight())));
    }

    @Test
    public void itemCounter() {
        shouldHaveParameter(geoItem, having(on(GeoItem.class).getCounter(), equalTo(geoExport.getCounter())));
    }

    @Test
    public void itemUrl() throws IOException {
        shouldHaveParameter(geoItem, having(on(GeoItem.class).getUrl(), equalTo(geoExport.getUrl())));
        shouldHaveResponseCode(client, normalizeUrl(geoItem.getUrl()), userAgent, equalTo(200));
    }

    @Test
    public void hasMetroIcon() {
        shouldHaveParameter(geoItem, having(on(GeoItem.class).getIcon(), equalTo(geoExport.getIcon())));
    }
}
