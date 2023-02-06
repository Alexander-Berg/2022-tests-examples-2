package ru.yandex.autotests.morda.api.search.v2;

import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.api.search.SearchApiRequest;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.restassured.requests.TypifiedRestAssuredRequest;
import ru.yandex.geobase.regions.Russia;

import java.util.stream.Collectors;

import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: lanqu
 * Date: 24.04.13
 */
public class SearchApiV2Request
        extends TypifiedRestAssuredRequest<SearchApiV2Request, SearchApiV2Response>
        implements SearchApiRequest<SearchApiV2Request> {

    private SearchApiRequestData requestData;

    public SearchApiV2Request(String environment) {
        this(environment, SearchApiBlock.ALL);
    }

    public SearchApiV2Request(String environment, SearchApiBlock block) {
        this(environment, new SearchApiRequestData().setBlock(block));
    }

    public SearchApiV2Request(String environment, SearchApiRequestData requestData) {
        super(SearchApiV2Response.class, desktopMain(environment).region(Russia.MOSCOW).getUrl());
        this.requestData = requestData;
        path("portal/api/search/2")
                .path(requestData.getBlock().getValue())
                .addDeserializer(SearchApiV2Response.class, new SearchApiV2Deserializer());
        queryParam("app_platform", "android");
        if (requestData.getAppVersion() != null) {
            queryParam("app_version", requestData.getAppVersion());
        }
        populateFromRequestData(this.requestData);
    }

    @Override
    public SearchApiV2Request me() {
        return this;
    }

    @Override
    public String toString() {
        String queryParamsString = queryParams.entrySet().stream()
                .map(e -> e.getKey() + "=" + e.getValue())
                .collect(Collectors.joining("; "));
        return requestData.getBlock().getValue() + "; " + queryParamsString;
    }

    @Override
    public SearchApiRequestData getRequestData() {
        return requestData;
    }
}
