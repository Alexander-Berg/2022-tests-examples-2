package ru.yandex.autotests.morda.data.afisha.searchapi;

import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.afisha.AfishaApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.afisha.AfishaApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.afisha.AfishaApiV2Event;
import ru.yandex.autotests.morda.beans.exports.afisha_geo_v2.AfishaGeoV2Entry;
import ru.yandex.autotests.morda.beans.exports.afisha_geo_v2.AfishaGeoV2Export;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;
import ru.yandex.autotests.morda.matchers.url.UrlMatcher;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.core.UriBuilder;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.on;
import static java.util.stream.Collectors.toSet;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.YellowskinMatcher.yellowskin;
import static ru.yandex.autotests.morda.matchers.string.RegexMatcher.regex;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class AfishaSearchApiV2Data {
    private static final AfishaGeoV2Export AFISHA_GEO_V_2_EXPORT = new AfishaGeoV2Export().populate();

    private static final String PRIMARY_COLOR = "#b00000";
    private static final String SECONDARY_COLOR = "#ffffff";

    private SearchApiRequestData requestData;

    public AfishaSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    public GeobaseRegion getAfishaApiV2Region() {
        List<AfishaGeoV2Entry> entries = AFISHA_GEO_V_2_EXPORT.find(MordaGeoFilter.filter(requestData.getGeo()));
        if (entries.isEmpty()) {
            return requestData.getGeo();
        } else {
            return new GeobaseRegion(entries.get(0).getShowGeo());
        }
    }

    public MordaDomain getDomain() {
        return MordaDomain.fromString(getAfishaApiV2Region().getKubrDomain());
    }

    public String getHost() {
        return UriBuilder.fromUri("https://afisha.yandex{domain}")
                .build(getDomain().getValue())
                .toString();
    }

    @Step("Check afisha")
    public void check(SearchApiV2Response response) {
        checkExists(response);
        checkBlock(response.getAfisha());
    }

    @Step("Check afisha block")
    public void checkBlock(AfishaApiV2 afisha) {

        checkBean(afisha, hasPropertyWithValue(on(AfishaApiV2.class).getTitle(),
                equalTo(TankerManager.get(ru.yandex.autotests.morda.tanker.home.Afisha.TITLE, requestData.getLanguage()))));

        checkData(afisha.getData());
    }

    @Step("Check afisha exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getAfisha(), notNullValue()));
    }

    @Step("Check data")
    public void checkData(AfishaApiV2Data data) {
        checkBean(data, allOfDetailed(
                hasPropertyWithValue(on(AfishaApiV2Data.class).getAfishaVersion(), equalTo(3)),
                hasPropertyWithValue(on(AfishaApiV2Data.class).getGeo(), equalTo(getAfishaApiV2Region().getRegionId()))
        ));
        checkEvents(data.getEvents());
    }

    @Step("Check events")
    public void checkEvents(List<AfishaApiV2Event> events) {
        for (int i = 0; i != events.size(); i++) {
            checkEvent(i, events.get(i));
        }

        checkPosters(events);
    }

    @Step("Check posters")
    public void checkPosters(List<AfishaApiV2Event> events) {
        List<String> firstScreenPosters = events.stream().limit(3)
                .map(AfishaApiV2Event::getPoster).collect(Collectors.toList());


        assertThat("No poster in first screen", firstScreenPosters.contains(null), is(false));
    }

    @Step("Check tabs [{0}]")
    public void checkEvent(int pos, AfishaApiV2Event event) {
        checkBean(event, getEventMatcher(event));
    }

    public Matcher<AfishaApiV2Event> getEventMatcher(AfishaApiV2Event event) {
        return allOfDetailed(
                hasPropertyWithValue(on(AfishaApiV2Event.class).getPoster(), getPosterUrlMatcher()),
                hasPropertyWithValue(on(AfishaApiV2Event.class).getUrl(),
                        yellowskin(PRIMARY_COLOR, SECONDARY_COLOR, getAfishaApiV2EventUrlMatcher(event))
                )
        );
    }

    public UrlMatcher getAfishaApiV2EventUrlMatcher(AfishaApiV2Event event) {
        return urlMatcher(getHost())
                .path("events/" + event.getEventId())
                .query("city", not(isEmptyOrNullString()))
                .query("appsearch_header", "1")
                .query("version", "mobile")
                .query("utm_source", "yandex_search_app")
                .query("utm_medium", "yamain_afisha");
    }

    public Matcher<String> getPosterUrlMatcher() {
        return anyOf(
                nullValue(),
                urlMatcher("https://avatars.mds.yandex.net/")
                        .path(regex(Pattern.compile("get-afishanew/\\w+/\\w+/960x690_noncrop")))
        );
    }

    @Step("Ping")
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        AfishaApiV2Data afisha = response.getAfisha().getData();

        Set<String> urls = new HashSet<>();

        urls.add(afisha.getUrl());

        afisha.getEvents().forEach(event -> {
            urls.add(SearchApiDataUtils.getYellowskinkUrl(event.getUrl()));
        });

        Set<String> normalizedUrls = urls.stream().map(SearchApiDataUtils::getYellowskinkUrl).collect(toSet());

        LinkUtils.ping(normalizedUrls, requestData.getGeo(), requestData.getLanguage());
    }

    @Step("Ping")
    public void pingStatic(SearchApiV2Response response) {
        checkExists(response);
        AfishaApiV2Data afisha = response.getAfisha().getData();

        Set<String> urls = new HashSet<>();

        afisha.getEvents().forEach(event -> {
            urls.add(event.getPoster());
        });

        LinkUtils.ping(urls, requestData.getGeo(), requestData.getLanguage());
    }

}
