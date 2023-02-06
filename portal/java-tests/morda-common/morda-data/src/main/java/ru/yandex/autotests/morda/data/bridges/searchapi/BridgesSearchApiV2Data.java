package ru.yandex.autotests.morda.data.bridges.searchapi;

import org.hamcrest.Matcher;
import org.joda.time.LocalDateTime;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.bridges.BridgesApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.bridges.BridgesApiV2Item;
import ru.yandex.autotests.morda.beans.exports.bridges.BridgesEntry;
import ru.yandex.autotests.morda.beans.exports.bridges.BridgesExport;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.autotests.morda.tanker.home.Bridges;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static ch.lambdaj.Lambda.on;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.ViewportMatcher.viewport;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/10/16
 */
public class BridgesSearchApiV2Data {
    private BridgesExport bridgesExport = new BridgesExport().populate();
    private SearchApiRequestData requestData;

    public BridgesSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    @Step("Check bridges")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkData(response.getBridges().getData());
    }

    @Step("Check bridges exist")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getBridges(), notNullValue()));
    }

    @Step("Check data")
    public void checkData(BridgesApiV2Data data) {
        checkBean(data, allOfDetailed(
                hasPropertyWithValue(on(BridgesApiV2Data.class).getTitle(),
                        equalTo(TankerManager.get(Bridges.TITLE, requestData.getLanguage())))
        ));
        checkItems0(data.get0());
        checkItems1(data.get1());
    }

    @Step("Check bridges items \"0\"")
    public void checkItems0(List<BridgesApiV2Item> items) {
        for (BridgesApiV2Item item : items) {
            checkItem(item.getBridgeName(), item);
        }

        List<String> expected = bridgesExport.find(e -> e.getFrom() != null && e.getBridgePriority().equals("0")).stream()
                .map(BridgesEntry::getBridgeId)
                .collect(toList());

        checkBridgesApiV2List(items, expected);
    }

    @Step("Check bridges items \"1\"")
    public void checkItems1(List<BridgesApiV2Item> items) {
        for (BridgesApiV2Item item : items) {
            checkItem(item.getBridgeName(), item);
        }

        List<String> expected = bridgesExport.find(e -> e.getFrom() != null && e.getBridgePriority().equals("1"))
                .stream()
                .map(BridgesEntry::getBridgeId)
                .collect(toList());

        checkBridgesApiV2List(items, expected);
    }

    @Step("Check bridges list")
    public void checkBridgesApiV2List(List<BridgesApiV2Item> items, List<String> expected) {
        List<String> actual = items.stream().map(BridgesApiV2Item::getBridgeId).collect(toList());
        checkBean(actual, hasSameItemsAsList(expected));
    }

    @Step("Check bridge \"{0}\"")
    public void checkItem(String id, BridgesApiV2Item item) {
        checkBean(item, getItemMatcher(item.getBridgeId()));
    }

    public Matcher<BridgesApiV2Item> getItemMatcher(String id) {

        BridgesEntry entry = bridgesExport.find(e -> e.getFrom() != null && e.getBridgeId().equals(id)).get(0);

        LocalDateTime lower1 = LocalDateTime.now()
                .plusDays(1)
                .withHourOfDay(entry.getBridgeLower1().getHourOfDay())
                .withMinuteOfHour(entry.getBridgeLower1().getMinuteOfHour())
                .minusHours(3);

        LocalDateTime up1 = LocalDateTime.now()
                .plusDays(1)
                .withHourOfDay(entry.getBridgeRaise1().getHourOfDay())
                .withMinuteOfHour(entry.getBridgeRaise1().getMinuteOfHour())
                .minusHours(3);

        String pattern = "%04d-%02d-%02dT%02d:%02d:00Z+0000";

        Matcher<String> lower1Matcher = equalTo(String.format(pattern,
                lower1.getYear(),
                lower1.getMonthOfYear(),
                lower1.getDayOfMonth(),
                lower1.getHourOfDay(),
                lower1.getMinuteOfHour()
        ));

        Matcher<String> raise1Matcher = equalTo(String.format(pattern,
                up1.getYear(),
                up1.getMonthOfYear(),
                up1.getDayOfMonth(),
                up1.getHourOfDay(),
                up1.getMinuteOfHour()
        ));

        AllOfDetailedMatcher<BridgesApiV2Item> matcher = allOfDetailed(
                hasPropertyWithValue(on(BridgesApiV2Item.class).getBridgeName(), equalTo(
                        TankerManager.get("home", "bridges", id.replace("bridges.", ""), requestData.getLanguage())
                )),
                hasPropertyWithValue(on(BridgesApiV2Item.class).getUrl(),
                        viewport(equalTo("serp"), not(isEmptyOrNullString()))
                ),
                hasPropertyWithValue(on(BridgesApiV2Item.class).getBridgeLower1Dt(), lower1Matcher),
                hasPropertyWithValue(on(BridgesApiV2Item.class).getBridgeRaise1Dt(), raise1Matcher)
        );
        
        if (entry.getBridgeRaise2() != null && entry.getBridgeLower2() != null) {
            LocalDateTime lower2 = LocalDateTime.now()
                    .plusDays(1)
                    .withHourOfDay(entry.getBridgeLower2().getHourOfDay())
                    .withMinuteOfHour(entry.getBridgeLower2().getMinuteOfHour())
                    .minusHours(3);

            LocalDateTime up2 = LocalDateTime.now()
                    .plusDays(1)
                    .withHourOfDay(entry.getBridgeRaise2().getHourOfDay())
                    .withMinuteOfHour(entry.getBridgeRaise2().getMinuteOfHour())
                    .minusHours(3);
            
            Matcher<String> lower2Matcher = equalTo(String.format(pattern,
                    lower2.getYear(),
                    lower2.getMonthOfYear(),
                    lower2.getDayOfMonth(),
                    lower2.getHourOfDay(),
                    lower2.getMinuteOfHour()
            ));

            Matcher<String> raise2Matcher = equalTo(String.format(pattern,
                    up2.getYear(),
                    up2.getMonthOfYear(),
                    up2.getDayOfMonth(),
                    up2.getHourOfDay(),
                    up2.getMinuteOfHour()
            ));

            matcher.and(
                    hasPropertyWithValue(on(BridgesApiV2Item.class).getBridgeLower2Dt(), lower2Matcher),
                    hasPropertyWithValue(on(BridgesApiV2Item.class).getBridgeRaise2Dt(), raise2Matcher)
            );
        } else {

            matcher.and(
                    hasPropertyWithValue(on(BridgesApiV2Item.class).getBridgeLower2Dt(), nullValue()),
                    hasPropertyWithValue(on(BridgesApiV2Item.class).getBridgeRaise2Dt(), nullValue())
            );
        }

        return matcher;
    }


    @Step("Ping")
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        BridgesApiV2Data bridges = response.getBridges().getData();

        Set<String> urls = new HashSet<>();

        bridges.get0().forEach(event -> {
            urls.add(event.getUrl());
        });
        bridges.get1().forEach(event -> {
            urls.add(event.getUrl());
        });

        LinkUtils.ping(urls, requestData.getGeo(), requestData.getLanguage());
    }

}
