package ru.yandex.autotests.morda.data.tv.searchapi;

import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.tv.TvApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.tv.TvApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.tv.TvApiV2Program;
import ru.yandex.autotests.morda.beans.api.search.v2.tv.TvApiV2Tab;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.data.tv.TvTouchData;
import ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.autotests.morda.tanker.home.ApiSearch;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.core.UriBuilder;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static ch.lambdaj.Lambda.on;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.data.SearchApiDataUtils.getRandomElement;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.YellowskinMatcher.yellowskin;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/09/16
 */
public class TvSearchApiV2Data extends TvSearchApiData implements TvTouchData {

    private static final String PRIMARY_COLOR = "#42435e";
    private static final String SECONDARY_COLOR = "#ffffff";
    private SearchApiRequestData requestData;

    public TvSearchApiV2Data(SearchApiRequestData requestData) {
        super(requestData.getGeo());
        this.requestData = requestData;
    }

    @Override
    public String getUrl() {
        return UriBuilder.fromUri(super.getUrl())
                .queryParam("appsearch_header", "1")
                .build()
                .toString();
    }

    public List<TvApiV2Program> getPrograms(TvApiV2Tab tab) {
        return tab.getProgram().stream()
                .filter(e -> !"separator".equals(e.getType()))
                .collect(toList());
    }

    public TvApiV2Program getRandomProgram(TvApiV2Tab tab) {
        return getRandomElement(getPrograms(tab));
    }

    @Step("Check Tv")
    public void check(SearchApiV2Response response) {
        checkExists(response);
        checkBlock(response.getTv());
    }

    @Step("Check Block")
    public void checkBlock(TvApiV2 tv) {
        Matcher<TvApiV2> tvMatcher = allOfDetailed(
                hasPropertyWithValue(on(TvApiV2.class).getTtl(), greaterThan(0)),
                hasPropertyWithValue(on(TvApiV2.class).getTtv(), greaterThan(0)),
                hasPropertyWithValue(on(TvApiV2.class).getTitle(), equalTo(TankerManager.get(ApiSearch.TV_TITLE, requestData.getLanguage())))
        );

        checkBean(tv, tvMatcher);
        checkTvData(tv.getData());
    }

    @Step("Check Tv Data")
    public void checkTvData(TvApiV2Data tvData) {
        Matcher<TvApiV2Data> tvDataMatcher = allOfDetailed(
                hasPropertyWithValue(on(TvApiV2Data.class).getGeo(), equalTo(getTvRegion().getRegionId()))
//                ,
//                hasPropertyWithValue(on(TvData.class).getUrl(), yellowskin(PRIMARY_COLOR, SECONDARY_COLOR, super.getUrlMatcher()))
        );

        checkBean(tvData, tvDataMatcher);
        checkTabs(tvData.getTab());
    }

    @Step("Check tabs")
    public void checkTabs(List<TvApiV2Tab> tabs) {
        for (TvApiV2Tab tab : tabs) {
            checkTab(tab.getTitle(), tab);
        }
    }

    @Step("Check tab {0}")
    public void checkTab(String tabId, TvApiV2Tab tab) {
        checkBean(tab, getTabMatcher(tab));
        checkPrograms(tab, getPrograms(tab));
    }

    @Step("Check programs")
    public void checkPrograms(TvApiV2Tab tab, List<TvApiV2Program> items) {
        for (int i = 0; i != items.size(); i++) {
            checkProgram(i, tab, items.get(i));
        }
    }

    @Step("Check program [{0}]")
    public void checkProgram(int pos, TvApiV2Tab tab, TvApiV2Program program) {
        checkBean(program, getProgramMatcher(tab, program));
    }

    public Matcher<TvApiV2Program> getProgramMatcher(TvApiV2Tab tab, TvApiV2Program event) {
        AllOfDetailedMatcher<TvApiV2Program> eventMatcher = allOfDetailed(
                hasPropertyWithValue(on(TvApiV2Program.class).getTime(), getTimeMatcher()),
                hasPropertyWithValue(on(TvApiV2Program.class).getTtl(), greaterThan(0)),
                hasPropertyWithValue(on(TvApiV2Program.class).getUrl(),
                        yellowskin(PRIMARY_COLOR, SECONDARY_COLOR, getEventUrlMatcher(event.getProgramId(), event.getEventId())))
        );

        if (tab.getType().equals("now") || tab.getType().equals("evening")) {
            eventMatcher.and(
                    hasPropertyWithValue(on(TvApiV2Program.class).getChannel(), not(isEmptyOrNullString()))
            );
        }

        return eventMatcher;
    }


    public Matcher<TvApiV2Tab> getNowTabMatcher() {
        return allOfDetailed(
                hasPropertyWithValue(on(TvApiV2Tab.class).getTitle(), equalTo(TankerManager.get(ru.yandex.autotests.morda.tanker.home.Tv.TITLE_NOW2, requestData.getLanguage()))),
                hasPropertyWithValue(on(TvApiV2Tab.class).getType(), equalTo("now")),
                hasPropertyWithValue(on(TvApiV2Tab.class).getUrl(), yellowskin(PRIMARY_COLOR, SECONDARY_COLOR, super.getUrlMatcher()))
        );
    }

    public Matcher<TvApiV2Tab> getEveningTabMatcher() {
        return allOfDetailed(
                hasPropertyWithValue(on(TvApiV2Tab.class).getType(), equalTo("evening")),
                hasPropertyWithValue(on(TvApiV2Tab.class).getUrl(),
                        yellowskin(PRIMARY_COLOR, SECONDARY_COLOR, super.getUrlMatcher().query("period", "evening"))),
                hasPropertyWithValue(on(TvApiV2Tab.class).getTitle(),
                        equalTo(TankerManager.get(ru.yandex.autotests.morda.tanker.home.Tv.TITLE_EVENING, requestData.getLanguage())))
        );
    }

    public Matcher<TvApiV2Tab> getTabMatcher(TvApiV2Tab tvTab) {
        if (tvTab.getType().equals("now")) {
            return getNowTabMatcher();
        }

        if (tvTab.getType().equals("evening")) {
            return getEveningTabMatcher();
        }

        return allOfDetailed(
                hasPropertyWithValue(on(TvApiV2Tab.class).getTitle(), not(isEmptyOrNullString())),
                hasPropertyWithValue(on(TvApiV2Tab.class).getType(), equalTo("channel")),
                hasPropertyWithValue(on(TvApiV2Tab.class).getUrl(),
                        yellowskin(PRIMARY_COLOR, SECONDARY_COLOR, super.getChannelUrlMatcher()))
        );
    }

    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getTv(), notNullValue()));
    }

    @Step
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        TvApiV2Data tv = response.getTv().getData();

        Set<String> urls = new HashSet<>();

        urls.add(tv.getUrl());

        tv.getTab().forEach(tab -> {
            urls.add(tab.getUrl());
            urls.add(getRandomElement(getPrograms(tab)).getUrl());
        });

        Set<String> normalizedUrls = urls.stream().map(SearchApiDataUtils::getYellowskinkUrl).collect(toSet());

        LinkUtils.ping(normalizedUrls, requestData.getGeo(), requestData.getLanguage());
    }

}
