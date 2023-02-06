package ru.yandex.autotests.morda.data.topnews.searchapi.v2;

import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.topnews.TopnewsApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.topnews.TopnewsApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.topnews.TopnewsApiV2Item;
import ru.yandex.autotests.morda.beans.api.search.v2.topnews.TopnewsApiV2Tab;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static ch.lambdaj.Lambda.on;
import static java.util.stream.Collectors.toSet;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.data.SearchApiDataUtils.getRandomElement;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.YellowskinMatcher.yellowskin;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.matchers.url.UrlQueryMatcher.queryMatcher;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class TopnewsSearchApiV2Data {

    private static final String PRIMARY_COLOR = "#f3f1ed";
    private static final String SECONDARY_COLOR = "#000000";

    private SearchApiRequestData requestData;

    public TopnewsSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    public GeobaseRegion getRegion() {
        GeobaseRegion region;
        if (requestData.getGeo() != null) {
            region = requestData.getGeo();
        } else if (requestData.getGeoForCoords() != null) {
            region = requestData.getGeoForCoords();
        } else {
            throw new IllegalStateException("Need region for domain");
        }
        return region;
    }

    public MordaDomain getDomain() {
        return MordaDomain.fromString(getRegion().getKubrDomain());
    }

    public String getHost() {
        return UriBuilder.fromUri("https://m.news.yandex{domain}")
                .build(getDomain().getValue())
                .toString();
    }

    public Matcher<String> getNewsUrlMatcher() {
        return yellowskin(PRIMARY_COLOR, SECONDARY_COLOR,
                urlMatcher(getHost())
                        .query(queryMatcher()
                                .param("appsearch_header", "1")
                                .param("lang", requestData.getLanguage().getValue())
                        )
        );

    }

    public Matcher<String> getNewsTabUrlMatcher() {
        URI url = URI.create(getHost());
        return yellowskin(PRIMARY_COLOR, SECONDARY_COLOR,
                urlMatcher()
                        .scheme(url.getScheme())
                        .host(url.getHost())
                        .query(queryMatcher()
                                .param("appsearch_header", "1")
                        )
        );
    }

    public Matcher<String> getNewsItemUrlMatcher() {
        return yellowskin(PRIMARY_COLOR, SECONDARY_COLOR,
                urlMatcher(getHost())
                        .path("yandsearch")
                        .query(queryMatcher()
                                        .param("lr", String.valueOf(getRegion().getRegionId()))
                                        .param("from", not(isEmptyOrNullString()))
//                                .param("lang", "ru")
                                        .param("cl4url", not(isEmptyOrNullString()))
                                        .param("appsearch_header", "1")
                        )
        );
    }

    @Step("Check topnews")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkBean(response.getTopnews(), hasPropertyWithValue(
                on(TopnewsApiV2.class).getTitle(),
                equalTo(TankerManager.get(ru.yandex.autotests.morda.tanker.home.Topnews.TITLE, requestData.getLanguage()))
        ));

        checkData(response.getTopnews().getData());
    }

    @Step("Check topnews exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getTopnews(), notNullValue()));
    }

    @Step("Check data")
    public void checkData(TopnewsApiV2Data data) {
        checkBean(data, hasPropertyWithValue(on(TopnewsApiV2Data.class).getUrl(), getNewsUrlMatcher()));
        checkTabs(data.getTab());
    }

    @Step("Check tabs")
    public void checkTabs(List<TopnewsApiV2Tab> tabs) {
        for (TopnewsApiV2Tab tab : tabs) {
            checkTab(tab.getTitle(), tab);
        }
    }

    @Step("Check tabs {0}")
    public void checkTab(String tabId, TopnewsApiV2Tab tab) {
        checkBean(tab, allOfDetailed(
                hasPropertyWithValue(on(TopnewsApiV2Tab.class).getUrl(), getNewsTabUrlMatcher())
        ));
        checkNews(tab.getNews());
    }

    @Step("Check news")
    public void checkNews(List<TopnewsApiV2Item> items) {
        for (int i = 0; i != items.size(); i++) {
            checkNewsItem(i, items.get(i));
        }
    }

    @Step("Check news [{0}]")
    public void checkNewsItem(int pos, TopnewsApiV2Item item) {
        checkBean(item, hasPropertyWithValue(on(TopnewsApiV2Item.class).getUrl(), getNewsItemUrlMatcher()));
    }

    @Step
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        TopnewsApiV2Data topnews = response.getTopnews().getData();

        Set<String> urls = new HashSet<>();

        urls.add(topnews.getUrl());

        topnews.getTab().forEach(tab -> {
            urls.add(tab.getUrl());
            urls.add(getRandomElement(tab.getNews()).getUrl());
        });

        Set<String> normalizedUrls = urls.stream().map(SearchApiDataUtils::getYellowskinkUrl).collect(toSet());


        LinkUtils.ping(normalizedUrls, requestData.getGeo(), requestData.getLanguage());
    }

}
