package ru.yandex.autotests.morda.restassured.requests;


import com.jayway.restassured.response.Response;

import static ru.yandex.autotests.morda.restassured.requests.RequestHelpers.wrapStep;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public interface GetRequest<T extends GetRequest<T>> extends Request<T> {

    default Response invoke() {
        return wrapStep("GET " + getUri().getPath(), () -> createRequestSpecification().get());
    }
}
