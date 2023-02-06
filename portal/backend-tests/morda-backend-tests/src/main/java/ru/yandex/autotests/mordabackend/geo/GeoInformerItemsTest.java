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
import ru.yandex.autotests.mordaexportsclient.beans.GeoInformerEntry;
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
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.YYYYMMDD;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 10.07.2014
 */
@Aqua.Test(title = "Geo Informer")
@Features("Geo")
@Stories("Geo Informer")
@RunWith(CleanvarsParametrizedRunner.class)
public class GeoInformerItemsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(GEO_REGIONS_MAIN)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34)
                    .withParameterProvider(new GeoParametrProvider(INFORMER))
                    .withCleanvarsBlocks(YYYYMMDD, GEO);

    private Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private GeoItem infoItem;
    private GeoServicesV14Entry geoServiceExport;
    private GeoInformerEntry geoInformerEntry;

    public GeoInformerItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                Language language, UserAgent userAgent, String informerItemId, GeoItem infoItem) {
        this.client = client;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.infoItem = infoItem;
        this.geoServiceExport = getGeoService(informerItemId, region.getDomain(), language, region);
        this.geoInformerEntry =
                getInformerGeoEntry(infoItem.getText(), region.getDomain(), language, region, cleanvars.getYYYYMMDD());
    }

    @Before
    public void preCheck() {
        assertThat("Нет соответствующего экспорта geo_informer для: " + infoItem, geoInformerEntry, notNullValue());
    }

    @Test
    public void itemUrl() throws IOException {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getRawUrl(), equalTo(geoInformerEntry.getUrl())));
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getUrl(),
                equalTo(geoInformerEntry.getUrl().replace("&", "&amp;"))));
        shouldHaveResponseCode(client,
                infoItem.getUrl().replace(" ", "%20").replace("|", "%7C"), userAgent, equalTo(200));
    }

    @Test
    public void itemFrom() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getFrom(), equalTo(geoInformerEntry.getFrom())));
    }

    @Test
    public void itemTill() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getTill(), equalTo(geoInformerEntry.getTill())));
    }

    @Test
    public void itemNewto() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getNewto(), equalTo(geoInformerEntry.getNewto())));
    }

    @Test
    public void itemText() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getText(), equalTo(geoInformerEntry.getText())));
    }

    //Same in GeoItemsTest
    @Test
    public void itemDomain() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getDomain(), equalTo(geoInformerEntry.getDomain())));
    }

    @Test
    public void itemGeo() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getGeo(), equalTo(geoInformerEntry.getGeo())));
    }

    @Test
    public void itemLanguage() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getLang(), equalTo(geoInformerEntry.getLang())));
    }

    @Test
    public void serviceName() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getService(), equalTo(geoServiceExport.getService())));
    }

    @Test
    public void serviceIcon() {
        shouldHaveParameter(infoItem,
                having(on(GeoItem.class).getServiceIcon(), equalTo(geoServiceExport.getServiceIcon())));
    }

    @Test
    public void serviceLink() {
        shouldHaveParameter(infoItem,
                having(on(GeoItem.class).getServiceLink(), equalTo(geoServiceExport.getServiceLink())));
    }

    @Test
    public void serviceWeight() {
        shouldHaveParameter(infoItem,
                having(on(GeoItem.class).getServiceWeight(), equalTo(geoServiceExport.getServiceWeight())));
    }

    @Test
    public void itemCounter() {
        shouldHaveParameter(infoItem, having(on(GeoItem.class).getCounter(), equalTo(geoInformerEntry.getCounter())));
    }
}
