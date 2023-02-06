package ru.yandex.autotests.morda.data.transportmap.searchapi;

import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.transportmap.TransportMapApiV2Data;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13/10/16
 */
public class TransportMapSearchApiV2Data {

    private SearchApiRequestData requestData;

    public TransportMapSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    @Step("Check transportmap")
    public void check(SearchApiV2Response response) {
        checkExists(response);

//        checkData(response.getServices().getData());
    }


    @Step("Check transportmap exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getTransportmap(), notNullValue()));
    }

    @Step("Ping urls")
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        TransportMapApiV2Data transportMap = response.getTransportmap().getData();

        Set<String> urls = new HashSet<>();

        urls.add(transportMap.getMapUrl());
        urls.add(SearchApiDataUtils.getFallbackUrl(transportMap.getFallbackUrl()));
        transportMap.getGroups().forEach(e -> urls.add(e.getUrl()));

        Set<String> normalizedUrls = urls.stream()
                .filter(e -> e != null && !e.startsWith("mapkit"))
                .map(SearchApiDataUtils::getFallbackUrl).collect(Collectors.toSet());

        LinkUtils.ping(normalizedUrls, requestData.getGeo(), requestData.getLanguage());
    }

}
