package ru.yandex.autotests.morda.restassured.requests;

import java.net.URI;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public class TypifiedRestAssuredGetRequest<RES>
        extends TypifiedRestAssuredRequest<TypifiedRestAssuredGetRequest<RES>, RES>
        implements GetRequest<TypifiedRestAssuredGetRequest<RES>> {

    public TypifiedRestAssuredGetRequest(Class<RES> responseClass, String host) {
        super(responseClass, host);
    }

    public TypifiedRestAssuredGetRequest(Class<RES> responseClass, URI host) {
        super(responseClass, host);
    }

    @Override
    public TypifiedRestAssuredGetRequest<RES> me() {
        return this;
    }
}
