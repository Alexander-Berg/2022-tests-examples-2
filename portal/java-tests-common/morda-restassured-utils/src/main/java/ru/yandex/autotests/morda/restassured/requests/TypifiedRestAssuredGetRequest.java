package ru.yandex.autotests.morda.restassured.requests;

import java.net.URI;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public class TypifiedRestAssuredGetRequest<T>
        extends TypifiedRestAssuredRequest<TypifiedRestAssuredGetRequest<T>, T>
        implements GetRequest<TypifiedRestAssuredGetRequest<T>> {

    public TypifiedRestAssuredGetRequest(Class<T> responseClass, String host) {
        super(responseClass, host);
    }

    public TypifiedRestAssuredGetRequest(Class<T> responseClass, URI host) {
        super(responseClass, host);
    }

    @Override
    public TypifiedRestAssuredGetRequest<T> me() {
        return this;
    }
}
