package ru.yandex.autotests.morda.data.stocks.searchapi.v2;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.stocks.StocksApiV2Data;
import ru.yandex.autotests.morda.beans.exports.stocks_defs.StocksDefsExport;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.exports.filters.MordaContentFilter;
import ru.yandex.autotests.morda.exports.filters.MordaDomainFilter;
import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;
import ru.yandex.autotests.morda.pages.MordaContent;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

import static ch.lambdaj.Lambda.on;
import static java.util.stream.Collectors.toSet;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.YellowskinMatcher.yellowskin;
import static ru.yandex.autotests.morda.matchers.string.RegexMatcher.regex;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.matchers.url.UrlQueryMatcher.queryMatcher;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class StocksSearchApiV2Data {

    private static final String PRIMARY_COLOR = "#000000";
    private static final String SECONDARY_COLOR = "#ffffff";

    private SearchApiRequestData requestData;

    public StocksSearchApiV2Data(SearchApiRequestData requestData) {
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

    public List<Integer> getStocks() {
        StocksDefsExport stocksDefsExport = new StocksDefsExport().populate();

//        new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(

        return stocksDefsExport.find(
                MordaDomainFilter.filter(getDomain()),
                MordaGeoFilter.filter(getRegion()),
                MordaContentFilter.filter(MordaContent.TOUCH)
        ).get(0).getStocks();

//        System.out.println(stocks);
//        StocksExport stocksExport = new StocksExport().populate();
//
//        for (int i : stocks) {
//            StocksEntry entry = stocksExport.find(e -> e.getId().equals("" +i)).get(0);
//            System.out.println(i + " " + entry.getType() + " " + entry.getText());
//        }

    }

    public static void main(String[] args) throws JsonProcessingException {
        StocksSearchApiV2Data data = new StocksSearchApiV2Data(new SearchApiRequestData().setGeo(Russia.MOSCOW));

        data.getStocks();
    }

    public MordaDomain getDomain() {
        return MordaDomain.fromString(getRegion().getKubrDomain());
    }

    public String getHost() {
        return UriBuilder.fromUri("https://m.news.yandex{domain}")
                .build(getDomain().getValue())
                .toString();
    }

    public Matcher<String> getCurrencyUrlMatcher() {
        return urlMatcher(getHost())
                .path(regex(Pattern.compile("quotes/.+\\.html")))
                .query(queryMatcher()
                        .param("appsearch_header", "1")
                );
    }

    public Matcher<String> getCashUrlMatcher() {
        return urlMatcher(getHost())
                .path(regex(Pattern.compile("quotes/" + getRegion().getRegionId() + "/.+\\.html")))
                .query(queryMatcher()
                        .param("appsearch_header", "1")
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
                                .param("lang", "ru")
                                .param("cl4url", not(isEmptyOrNullString()))
                                .param("appsearch_header", "1")
                        )
        );
    }
//
//    @Step("Check stocks")
//    public void check(SearchApiV2Response response) {
//        checkExists(response);
//        checkData(response.getStocks().getData());
//    }
//
    @Step("Check stocks exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getStocks(), notNullValue()));
    }

//    @Step("Check data")
//    public void checkData(StocksData data) {
////        checkBean(data, hasPropertyWithValue(on(TopnewsData.class).getUrl(), getNewsUrlMatcher()));
////        checkTabs(data.getTab());
//    }
//
//    @Step("Check tabs")
//    public void checkTabs(List<TopnewsTab> tabs) {
//        for (TopnewsTab tab : tabs) {
//            checkTab(tab.getTitle(), tab);
//        }
//    }
//
//    @Step("Check tabs {0}")
//    public void checkTab(String tabId, TopnewsTab tab) {
//        checkBean(tab, allOfDetailed(
//                hasPropertyWithValue(on(TopnewsTab.class).getUrl(), getNewsTabUrlMatcher())
//        ));
//        checkNews(tab.getNews());
//    }
//
//    @Step("Check news")
//    public void checkNews(List<TopnewsItem> items) {
//        for (int i = 0; i != items.size(); i++) {
//            checkNewsItem(i, items.get(i));
//        }
//    }
//
//    @Step("Check news [{0}]")
//    public void checkNewsItem(int pos, TopnewsItem item) {
//        checkBean(item, hasPropertyWithValue(on(TopnewsItem.class).getUrl(), getNewsItemUrlMatcher()));
//    }

    @Step
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        StocksApiV2Data stocks = response.getStocks().getData();

        Set<String> urls = new HashSet<>();

        stocks.getGroups().forEach(group -> {
            group.getRows().forEach(e -> urls.add(e.getUrl()));
        });

        Set<String> normalizedUrls = urls.stream().map(SearchApiDataUtils::getYellowskinkUrl).collect(toSet());

        LinkUtils.ping(normalizedUrls, requestData.getGeo(), requestData.getLanguage());
    }

}
