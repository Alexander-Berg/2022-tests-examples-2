package ru.yandex.autotests.morda.restassured.requests;


import com.jayway.restassured.response.Response;

import java.util.function.Supplier;

import static ru.yandex.autotests.morda.restassured.requests.RequestHelpers.wrapStep;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public interface GetRequest<REQ extends GetRequest<REQ>> extends Request<REQ> {

    default Response invoke() {
        Supplier<Response> request = () -> createRequestSpecification().get();

        if (isSilent()) {
            return request.get();
        }
        return wrapStep("GET " + getUri(), request);
    }
}
