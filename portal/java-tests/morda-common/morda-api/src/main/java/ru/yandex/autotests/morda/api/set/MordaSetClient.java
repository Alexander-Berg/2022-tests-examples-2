package ru.yandex.autotests.morda.api.set;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.restassured.filters.RestAssuredCookieStorageFilter;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredPostRequest;

import java.net.URI;

/**
 * User: asamar
 * Date: 31.10.16
 */
public class MordaSetClient {

    private RestAssuredCookieStorageFilter cookieStorage;
    private URI host;

    public MordaSetClient(URI host, RestAssuredCookieStorageFilter cookieStorage) {
        this.host = host;
        this.cookieStorage = cookieStorage;
    }

    public RestAssuredGetRequest lang(String sk, MordaLanguage language, String retpath) {
        return lang(sk, language.getValue(), retpath);
    }

    public RestAssuredGetRequest lang(String sk, String language, String retpath) {
        return new RestAssuredGetRequest(host)
                .cookieStorage(cookieStorage)
                .followRedirects(false)
                .path("/portal/set/lang/")
                .queryParam("sk", sk)
                .queryParam("intl", language)
                .queryParam("retpath", retpath);
    }

    public RestAssuredGetRequest any(String sk, String paramName, String paramValue, String retpath) {
        return new RestAssuredGetRequest(host)
                .cookieStorage(cookieStorage)
                .followRedirects(false)
                .path("/portal/set/any/")
                .queryParam("sk", sk)
                .queryParam(paramName, paramValue)
                .queryParam("retpath", retpath)
                .queryParam("empty", "1");
    }

    public RestAssuredGetRequest my(String sk, String param1, String param2, String block, String retpath) {
        return new RestAssuredGetRequest(host)
                .cookieStorage(cookieStorage)
                .followRedirects(false)
                .path("/portal/set/my/")
                .queryParam("sk", sk)
                .queryParam("param", param1)
                .queryParam("param", param2)
                .queryParam("block", block)
                .queryParam("retpath", retpath);
    }

    public RestAssuredGetRequest my(String sk, String param, String block, String retpath) {
        return new RestAssuredGetRequest(host)
                .cookieStorage(cookieStorage)
                .followRedirects(false)
                .path("/portal/set/my/")
                .queryParam("sk", sk)
                .queryParam("param", param)
                .queryParam("block", block)
                .queryParam("retpath", retpath);
    }

    public RestAssuredGetRequest my(String sk, String param, String retpath) {
        return new RestAssuredGetRequest(host)
                .cookieStorage(cookieStorage)
                .followRedirects(false)
                .path("/portal/set/my/")
                .queryParam("sk", sk)
                .queryParam("param", param)
                .queryParam("retpath", retpath);
    }

    public RestAssuredGetRequest tuneGet(String sk, String name, String value, String retpath) {
        return new RestAssuredGetRequest(host)
                .cookieStorage(cookieStorage)
                .followRedirects(false)
                .path("/portal/set/tune/")
                .queryParam("sk", sk)
                .queryParam(name, value)
                .queryParam("retpath", retpath);
    }

    public RestAssuredPostRequest<String> tunePost(String sk, String name, String value, String retpath) {
        String postPattern = "%s=%s&fields=%s&sk=%s&retpath=%s";
        String postData = String.format(postPattern, name, value, name, sk, retpath);
        return new RestAssuredPostRequest<String>(host)
                .contentType("application/x-www-form-urlencoded")
                .cookieStorage(cookieStorage)
                .followRedirects(false)
                .path("/portal/set/tune/")
                .post(postData);
    }
}
