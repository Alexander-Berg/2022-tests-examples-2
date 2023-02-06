package ru.yandex.autotests.morda.api.search;

import ru.yandex.autotests.morda.api.search.v1.SearchApiV1Request;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 03/10/16
 */
public class SearchApiClient {

    public SearchApiRequest request(String environment, SearchApiRequestData requestData) {
        if (requestData.getVersion() == SearchApiVersion.v1) {
            return v1(environment, requestData);
        } else if (requestData.getVersion() == SearchApiVersion.v2) {
            return v2(environment, requestData);
        } else {
            throw new IllegalArgumentException("Unknown api version: " + requestData.getVersion());
        }
    }

    public SearchApiV1Request v1(String environment) {
        return new SearchApiV1Request(environment);
    }

    public SearchApiV1Request v1(String environment, SearchApiBlock block) {
        return new SearchApiV1Request(environment, block);
    }

    public SearchApiV1Request v1(String environment, SearchApiRequestData requestData) {
        return new SearchApiV1Request(environment, requestData);
    }

    public SearchApiV2Request v2(String environment) {
        return new SearchApiV2Request(environment);
    }

    public SearchApiV2Request v2(String environment, SearchApiBlock block) {
        return new SearchApiV2Request(environment, block);
    }

    public SearchApiV2Request v2(String environment, SearchApiRequestData requestData) {
        return new SearchApiV2Request(environment, requestData);
    }

}
