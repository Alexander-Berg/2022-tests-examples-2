package ru.yandex.autotests.morda.restassured.requests;

import java.net.URI;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public class RestAssuredGetRequest extends RestAssuredRequest<RestAssuredGetRequest>
        implements GetRequest<RestAssuredGetRequest> {

    public RestAssuredGetRequest(String baseUri) {
        super(baseUri);
    }

    public RestAssuredGetRequest(URI baseUri) {
        super(baseUri);
    }

    @Override
    public RestAssuredGetRequest me() {
        return this;
    }
}
