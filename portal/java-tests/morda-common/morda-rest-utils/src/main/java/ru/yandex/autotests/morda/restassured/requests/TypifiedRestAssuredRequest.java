package ru.yandex.autotests.morda.restassured.requests;


import java.net.URI;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public abstract class TypifiedRestAssuredRequest<REQ extends TypifiedRestAssuredRequest<REQ, RES>, RES>
        extends RestAssuredRequest<REQ> {
    private Class<RES> responseClass;

    public TypifiedRestAssuredRequest(Class<RES> responseClass, String host) {
        super(host);
        this.responseClass = responseClass;
    }

    public TypifiedRestAssuredRequest(Class<RES> responseClass, URI host) {
        super(host);
        this.responseClass = responseClass;
    }

    public Class<RES> getResponseClass() {
        return responseClass;
    }

    public RES read() {
        return read(getResponseClass());
    }
}
