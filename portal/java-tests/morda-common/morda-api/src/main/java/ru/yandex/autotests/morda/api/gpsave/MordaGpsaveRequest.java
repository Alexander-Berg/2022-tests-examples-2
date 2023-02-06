package ru.yandex.autotests.morda.api.gpsave;

import ru.yandex.autotests.morda.beans.gpsave.MordaGpSaveResponse;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.restassured.requests.GetRequest;
import ru.yandex.autotests.morda.restassured.requests.TypifiedRestAssuredRequest;

import java.net.URI;

/**
 * User: lanqu
 * Date: 24.04.13
 */
public class MordaGpsaveRequest
        extends TypifiedRestAssuredRequest<MordaGpsaveRequest, MordaGpSaveResponse>
        implements GetRequest<MordaGpsaveRequest> {

    public MordaGpsaveRequest(String host) {
        super(MordaGpSaveResponse.class, host);
    }

    public MordaGpsaveRequest(URI host) {
        super(MordaGpSaveResponse.class, host);
        path("gpsave");
        queryParam("laas", "1");
    }

    @Override
    public MordaGpsaveRequest me() {
        return this;
    }

    public MordaGpsaveRequest withLat(double lat) {
        queryParam("lat", lat);
        return this;
    }

    public MordaGpsaveRequest withLon(double lon) {
        queryParam("lon", lon);
        return this;
    }

    public MordaGpsaveRequest withPrecision(int precision) {
        queryParam("precision", precision);
        return this;
    }

    public MordaGpsaveRequest withDevice(int device) {
        queryParam("device", device);
        return this;
    }

    public MordaGpsaveRequest withDevice(MordaGpsaveDevice device) {
        return withDevice(device.getValue());
    }

    public MordaGpsaveRequest withFormat(String format) {
        queryParam("format", format);
        return this;
    }

    public MordaGpsaveRequest withFormat(MordaGpsaveFormat format) {
        return withFormat(format.getValue());
    }

    public MordaGpsaveRequest withLang(String language) {
        queryParam("lang", language);
        return this;
    }

    public MordaGpsaveRequest withLang(MordaLanguage language) {
        return withLang(language.getValue());
    }

    public MordaGpsaveRequest withSk(String sk) {
        queryParam("sk", sk);
        return this;
    }
}
