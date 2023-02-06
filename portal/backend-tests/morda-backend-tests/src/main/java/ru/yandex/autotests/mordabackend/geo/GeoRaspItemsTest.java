package ru.yandex.autotests.mordabackend.geo;

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
import ru.yandex.autotests.mordaexportsclient.beans.GeoServicesV14Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isOneOf;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEO;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.GEO_REGIONS_MAIN;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.RASP;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.getGeoService;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 10.07.2014
 */
@Aqua.Test(title = "Geo Rasp")
@Features("Geo")
@Stories("Geo Rasp")
@RunWith(CleanvarsParametrizedRunner.class)
public class GeoRaspItemsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(GEO_REGIONS_MAIN)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34)
                    .withParameterProvider(new GeoParametrProvider(RASP))
                    .withCleanvarsBlocks(GEO);

    private Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private GeoItem raspItem;
    private GeoServicesV14Entry geoServiceExport;

    public GeoRaspItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                            Language language, UserAgent userAgent, String raspItemId, GeoItem raspItem) {
        this.client = client;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.raspItem = raspItem;
        this.geoServiceExport = getGeoService(raspItemId, region.getDomain(), language, region);
    }

    @Test
    public void hasBus() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getBus(), isOneOf(1, 0)));
    }

    @Test
    public void hasAero() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getAero(), isOneOf(1, 0)));
    }

    @Test
    public void hasEl() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getEl(), isOneOf(1, 0)));
    }

    @Test
    public void hasShip() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getShip(), isOneOf(1, 0)));
    }

    @Test
    public void hasTrain() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getTrain(), isOneOf(1, 0)));
    }

    //Same in GeoItemsTest
    @Test
    public void itemDomain() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getDomain(), equalTo(geoServiceExport.getDomain())));
    }

    @Test
    public void itemGeo() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getGeo(), notNullValue()));
    }

    @Test
    public void itemLanguage() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getLang(), equalTo(geoServiceExport.getLang())));
    }

    @Test
    public void serviceName() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getService(),
                equalTo(geoServiceExport.getService())));
    }

    @Test
    public void serviceIcon() {
        shouldHaveParameter(raspItem,
                    having(on(GeoItem.class).getServiceIcon(), equalTo(geoServiceExport.getServiceIcon())));
    }

    @Test
    public void serviceLink() {
        shouldHaveParameter(raspItem,
                having(on(GeoItem.class).getServiceLink(), equalTo(geoServiceExport.getServiceLink())));
    }

    @Test
    public void serviceWeight() {
        shouldHaveParameter(raspItem,
                having(on(GeoItem.class).getServiceWeight(), equalTo(geoServiceExport.getServiceWeight())));
    }

    @Test
    public void itemCounter() {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getCounter(), equalTo(geoServiceExport.getCounter())));
    }

    @Test
    public void itemUrl() throws IOException {
        shouldHaveParameter(raspItem, having(on(GeoItem.class).getUrl(), equalTo(geoServiceExport.getServiceLink())));
        addLink(raspItem.getUrl(), region, false, language, userAgent);
        shouldHaveResponseCode(client, normalizeUrl(raspItem.getUrl()), userAgent, equalTo(200));
    }
}
