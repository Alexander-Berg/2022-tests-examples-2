package ru.yandex.autotests.morda.data.transport.searchapi;

import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.search.SearchApiDp;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.transport.TransportApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.transport.TransportApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.transport.TransportApiV2Item;
import ru.yandex.autotests.morda.beans.exports.geo.GeoEntry;
import ru.yandex.autotests.morda.beans.exports.geo.GeoMetro2Export;
import ru.yandex.autotests.morda.beans.exports.geo.GeoTaxiExport;
import ru.yandex.autotests.morda.beans.exports.rasp.RaspEntry;
import ru.yandex.autotests.morda.beans.exports.rasp.RaspExport;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;
import ru.yandex.autotests.morda.exports.filters.MordaLanguageFilter;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.core.UriBuilder;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toSet;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.IntentMatcher.intent;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;
import static ru.yandex.autotests.morda.tanker.home.ApiSearch.TRANSPORT_TITLE;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/10/16
 */
public class TransportSearchApiV2Data {
    private SearchApiRequestData requestData;
    private static final GeoTaxiExport GEO_TAXI_EXPORT = new GeoTaxiExport().populate();
    private static final GeoMetro2Export GEO_METRO_2_EXPORT = new GeoMetro2Export().populate();
    private static final RaspExport RASP_EXPORT = new RaspExport().populate();

    public TransportSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    public Matcher<String> getIconUrlMatcher(String id) {
        SearchApiDp dp = requestData.getDp();
        if (dp == null) {
            dp = SearchApiDp._1;
        }

        return equalTo(String.format("https://api.yastatic.net/morda-logo/i/yandex-app/transport/%s.%s.png", id, dp.getValue()));
    }

    @Step("Check transport")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkBean(response.getTransport(), hasPropertyWithValue(
                on(TransportApiV2.class).getTitle(),
                equalTo(TankerManager.get(TRANSPORT_TITLE, requestData.getLanguage()))
        ));

        checkData(response.getTransport().getData());
    }

    @Step("Check transport exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getTransport(), notNullValue()));
    }

    @Step("Check data")
    public void checkData(TransportApiV2Data data) {
//        checkBean(data, hasPropertyWithValue(on(TransportData.class).getUrl(), getNewsUrlMatcher()));
        checkItems(data.getList());
    }

    @Step("Check transport items")
    public void checkItems(List<TransportApiV2Item> items) {
        for (TransportApiV2Item item : items) {
            checkItem(item.getId(), item);
        }

//        checkItemList(items);
    }


    @Step("Check transport items")
    public void checkItemList(List<TransportApiV2Item> items) {
        List<String> actual = items.stream().map(TransportApiV2Item::getId).collect(Collectors.toList());
        List<String> expected = new ArrayList<>();

        List<GeoEntry> taxi = GEO_TAXI_EXPORT.find(
                MordaGeoFilter.filter(requestData.getGeo()),
                MordaLanguageFilter.filter(requestData.getLanguage())
        );

        List<GeoEntry> metro= GEO_METRO_2_EXPORT.find(
                MordaGeoFilter.filter(requestData.getGeo())
        );

        if (!taxi.isEmpty()) {
            expected.add("taxi");
        }

        if (!metro.isEmpty()) {
            expected.add("metro");
        }

        List<RaspEntry> rasps = RASP_EXPORT.find(
                MordaGeoFilter.filter(requestData.getGeo())
        );

        if (rasps.isEmpty()) {
            throw new IllegalStateException("Failed to get rasp export data");
        }

        RaspEntry entry = null;

        for (int geo : requestData.getGeo().getParentsIds()) {
            Optional<RaspEntry> e = rasps.stream().filter(ee -> ee.getGeo().getRegion().getRegionId() == geo).findFirst();
            if (e.isPresent()) {
                entry = e.get();
                break;
            }
        }

        if (entry == null) {
            throw new IllegalStateException("Failed to get rasp export data");
        }

        if (entry.getAero() == 1) {
            expected.add("plane");
        }

        if (entry.getTrain() == 1) {
            expected.add("train");
        }

        if (entry.getBus() == 1) {
            expected.add("bus");
        }

        if (entry.getShip() == 1) {
            expected.add("water");
        }

        if (entry.getEl() == 1) {
            expected.add("suburban");
        }

        checkBean(actual, hasSameItemsAsList(expected));
    }


    @Step("Check transport item \"{0}\"")
    public void checkItem(String id, TransportApiV2Item item) {
        checkBean(item, getItemMatcher(id));
    }

    public Matcher<TransportApiV2Item> getItemMatcher(String id) {
        return allOfDetailed(
                hasPropertyWithValue(on(TransportApiV2Item.class).getIcon(), getIconUrlMatcher(id)),
                hasPropertyWithValue(on(TransportApiV2Item.class).getUrl(), getItemUrlMatcher(id)),
                hasPropertyWithValue(on(TransportApiV2Item.class).getTitle(), equalTo(
                        TankerManager.get("home", "api_search", "transport." + id, requestData.getLanguage())
                ))
        );
    }

    public String getRaspHost() {
        return UriBuilder.fromUri("https://t.rasp.yandex{domain}/")
                .build(requestData.getGeo().getKubrDomain())
                .toString();
    }

    public Matcher<String> getItemUrlMatcher(String id) {
        if (asList("plane", "bus", "train", "water").contains(id)) {
            return urlMatcher(getRaspHost())
                    .path("stations/" + id)
                    .query("city_geo_id", equalTo("" +requestData.getGeo().getRegionId()));
        }

        if (id.equals("taxi")) {
            MordaDomain mordaDomain = MordaDomain.fromString(requestData.getGeo().getKubrDomain());
            MordaDomain domain;

            switch (mordaDomain) {
                case UA: domain = MordaDomain.UA; break;
                case KZ: domain = MordaDomain.KZ; break;
                default: domain = MordaDomain.RU; break;
            }

            return intent()
                    .browserFallbackUrl(urlMatcher("https://taxi.yandex" + domain.getValue()))
                    .packageMatcher(equalTo("ru.yandex.taxi"));
        }

        if (id.equals("metro")) {
            GeoEntry entry = getMetroEntry();
            if (entry == null) fail("no metro needed");
            return intent()
                    .browserFallbackUrl(urlMatcher("https:" + entry.getUrl()))
                    .packageMatcher(equalTo("ru.yandex.metro"));
        }

        if (id.equals("suburban")) {

            return intent()
                    .browserFallbackUrl(urlMatcher(getRaspHost()).path("suburban-directions").query("city_geo_id", equalTo("" +requestData.getGeo().getRegionId())))
                    .packageMatcher(equalTo("ru.yandex.rasp"));
        }

        throw new IllegalStateException("Failed to get matcher for id " + id);
    }

    public GeoEntry getMetroEntry() {
        GeoMetro2Export metro2Export = new GeoMetro2Export().populate();

        List<GeoEntry> entry = metro2Export.find(MordaGeoFilter.filter(requestData.getGeo()));

        if (entry.isEmpty()) return null;

        return entry.get(0);
    }

    @Step
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        TransportApiV2Data transport = response.getTransport().getData();

        Set<String> urls = transport.getList().stream()
                .filter(e -> asList("plane", "bus", "train", "water").contains(e.getId()))
                .map(TransportApiV2Item::getUrl)
                .collect(toSet());

        LinkUtils.ping(urls, requestData.getGeo(), requestData.getLanguage());
    }

    @Step
    public void pingStatic(SearchApiV2Response response) {
        checkExists(response);
        TransportApiV2Data transport = response.getTransport().getData();

        Set<String> urls = transport.getList().stream().map(TransportApiV2Item::getIcon).collect(toSet());

        LinkUtils.ping(urls);
    }

}
