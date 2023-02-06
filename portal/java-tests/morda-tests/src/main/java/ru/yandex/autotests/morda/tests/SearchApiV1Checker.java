package ru.yandex.autotests.morda.tests;

import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v1.SearchApiV1Response;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/16
 */
public abstract class SearchApiV1Checker extends SearchApiChecker<SearchApiV1Response> {

    public SearchApiV1Checker(SearchApiRequestData requestData) {
        super(requestData);
    }
}
