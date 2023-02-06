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
import ru.yandex.autotests.mordaexportsclient.beans.Poi2Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.GEO;
import static ru.yandex.autotests.mordabackend.geo.GeoUtils.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 10.07.2014
 */
@Aqua.Test(title = "Geo Poi")
@Features("Geo")
@Stories("Geo Poi")
@RunWith(CleanvarsParametrizedRunner.class)
public class GeoPoiItemsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(GEO_REGIONS_MAIN)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34)
                    .withParameterProvider(new GeoParametrProvider(POI))
                    .withCleanvarsBlocks(GEO);

    private Client client;
    private Region region;
    private Language language;
    private GeoItem poiItem;
    private GeoServicesV14Entry geoServiceExport;
    private Poi2Entry poi2Entry;

    public GeoPoiItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                           Language language, UserAgent userAgent, String poiItemId, GeoItem poiItem) {
        this.client = client;
        this.region = region;
        this.language = language;
        this.poiItem = poiItem;
        this.geoServiceExport = getGeoService(poiItemId, region.getDomain(), language, region);
//        this.poi2Entry = getPoiGeoEntry(poiItem.getId());
    }

//    @Before
//    public void preCheck() {
//        assertThat("Нет соответствующего экспорта poi_2 для: " + poiItem, poi2Entry, notNullValue());
//    }
//
//    @Test
//    public void poiBig() {
//        shouldHaveParameter(poiItem, having(on(GeoItem.class).getBig(), equalTo(poi2Entry.getBig())));
//    }
//
//    @Test
//    public void poiPromo() {
//        shouldHaveParameter(poiItem, having(on(GeoItem.class).getPromo(), equalTo(poi2Entry.getPromo())));
//    }
//
//    @Test
//    public void poiDescription() {
//        shouldHaveParameter(poiItem, having(on(GeoItem.class).getDescription(),
//                equalTo(getTranslation("home", "mobile", "poi.category." + poi2Entry.getId(), language))));
//    }
//
//    @Test
//    public void poiText() {
//        shouldHaveParameter(poiItem, having(on(GeoItem.class).getText(),
//                equalTo(getTranslationSafely("home", "mobile", "poi.search." + poi2Entry.getId(), language))));
//    }
//
//    @Test
//    public void poiUrlTextPart() {
//        shouldHaveParameter(poiItem, having(on(GeoItem.class).getTextUri(),
//                equalTo(encodeRequest(
//                        getTranslationSafely("home", "mobile", "poi.search." + poi2Entry.getId(), language)))));
//    }

    @Test
    public void poiN() {
        shouldHaveParameter(poiItem, having(on(GeoItem.class).getN(), equalTo(20)));
    }

    //Same in GeoItemsTest
    @Test
    public void itemDomain() {
        shouldHaveParameter(poiItem, having(on(GeoItem.class).getDomain(), equalTo(geoServiceExport.getDomain())));
    }

    @Test
    public void itemGeo() {
        shouldHaveParameter(poiItem, having(on(GeoItem.class).getGeo(), equalTo(geoServiceExport.getGeo())));
    }

    @Test
    public void itemLanguage() {
        shouldHaveParameter(poiItem, having(on(GeoItem.class).getLang(), equalTo(geoServiceExport.getLang())));
    }

    @Test
    public void serviceName() {
        shouldHaveParameter(poiItem, having(on(GeoItem.class).getService(),
                equalTo(geoServiceExport.getService())));
    }

    @Test
    public void serviceIcon() {
        shouldHaveParameter(poiItem,
                having(on(GeoItem.class).getServiceIcon(), equalTo(geoServiceExport.getServiceIcon())));
    }

    @Test
    public void serviceLink() {
        shouldHaveParameter(poiItem,
                having(on(GeoItem.class).getServiceLink(), equalTo(geoServiceExport.getServiceLink())));
    }

    @Test
    public void serviceWeight() {
        shouldHaveParameter(poiItem,
                having(on(GeoItem.class).getServiceWeight(), equalTo(geoServiceExport.getServiceWeight())));
    }

//    @Test
//    public void itemCounter() {
//        shouldHaveParameter(poiItem, having(on(GeoItem.class).getCounter(),
//                isIn(extract(exports(POI_GEO, geo(region.getRegionIdInt())), on(PoiGeoEntry.class).getId()))));
//    }

    @Test
    public void itemUrl() throws IOException {
        shouldHaveParameter(poiItem, having(on(GeoItem.class).getUrl(), nullValue()));

    }
}
