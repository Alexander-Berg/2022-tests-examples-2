package ru.yandex.autotests.morda.api.search.v1;

import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.api.search.SearchApiRequest;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v1.SearchApiV1Response;
import ru.yandex.autotests.morda.restassured.requests.TypifiedRestAssuredRequest;
import ru.yandex.geobase.regions.Russia;

import java.util.stream.Collectors;

import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: lanqu
 * Date: 24.04.13
 */
public class SearchApiV1Request
        extends TypifiedRestAssuredRequest<SearchApiV1Request, SearchApiV1Response>
        implements SearchApiRequest<SearchApiV1Request> {

    private SearchApiRequestData requestData;

    public SearchApiV1Request(String environment) {
        this(environment, SearchApiBlock.ALL);
    }

    public SearchApiV1Request(String environment, SearchApiBlock block) {
        this(environment, new SearchApiRequestData().setBlock(block));
    }

    public SearchApiV1Request(String environment, SearchApiRequestData requestData) {
        super(SearchApiV1Response.class, desktopMain(environment).region(Russia.MOSCOW).getUrl());
        this.requestData = requestData;
        path("portal/api/search/1")
                .path(requestData.getBlock().getValue())
                .addDeserializer(SearchApiV1Response.class, new SearchApiV1Deserializer());
        queryParam("app_platform", "android");
        populateFromRequestData(this.requestData);
    }

    @Override
    public SearchApiV1Request me() {
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
