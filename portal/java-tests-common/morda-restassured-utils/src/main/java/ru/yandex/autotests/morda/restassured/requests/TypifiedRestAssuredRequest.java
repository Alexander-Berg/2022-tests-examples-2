package ru.yandex.autotests.morda.restassured.requests;


import java.net.URI;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public abstract class TypifiedRestAssuredRequest<T extends TypifiedRestAssuredRequest<T, E>, E>
        extends RestAssuredRequest<T> {
    private Class<E> responseClass;

    public TypifiedRestAssuredRequest(Class<E> responseClass, String host) {
        super(host);
        this.responseClass = responseClass;
    }

    public TypifiedRestAssuredRequest(Class<E> responseClass, URI host) {
        super(host);
        this.responseClass = responseClass;
    }

    public Class<E> getResponseClass() {
        return responseClass;
    }

    public E read() {
        return read(getResponseClass());
    }
}
