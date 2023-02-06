package ru.yandex.autotests.morda.api;

import com.jayway.restassured.RestAssured;
import com.jayway.restassured.parsing.Parser;
import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsRequest;
import ru.yandex.autotests.morda.api.gpsave.MordaGpsaveDevice;
import ru.yandex.autotests.morda.api.gpsave.MordaGpsaveFormat;
import ru.yandex.autotests.morda.api.gpsave.MordaGpsaveRequest;
import ru.yandex.autotests.morda.api.search.SearchApiClient;
import ru.yandex.autotests.morda.api.set.MordaSetClient;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.autotests.morda.restassured.filters.RestAssuredCookieStorageFilter;
import ru.yandex.autotests.morda.restassured.requests.Request.RequestAction;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
import ru.yandex.geobase.beans.GeobaseRegionData;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.morda.api.MordaRequestActions.authIfNeeded;
import static ru.yandex.autotests.morda.api.MordaRequestActions.setLanguageIfNeeded;
import static ru.yandex.autotests.morda.api.MordaRequestActions.setRegionIfNeeded;

/**
 * User: lanqu
 * Date: 24.04.13
 */
public class MordaClient {
    private static final Logger LOGGER = Logger.getLogger(MordaClient.class);

    static {
        RestAssured.registerParser("text/plain", Parser.JSON);
        RestAssured.registerParser("text/javascript", Parser.JSON);
    }

    private RestAssuredCookieStorageFilter cookieStorage;

    public MordaClient() {
        this(new RestAssuredCookieStorageFilter());
    }

    public MordaClient(RestAssuredCookieStorageFilter cookieStorage) {
        this.cookieStorage = cookieStorage;
    }

    public MordaCleanvarsRequest cleanvars(URI url) {
        return new MordaCleanvarsRequest(url)
                .cookieStorage(cookieStorage);
    }

    public MordaCleanvarsRequest cleanvars(Morda<?> morda) {
        return new MordaCleanvarsRequest(morda)
                .cookieStorage(cookieStorage);
    }

    public MordaCleanvarsRequest cleanvars(Morda<?> morda, String... blocks) {
        return new MordaCleanvarsRequest(morda, blocks)
                .cookieStorage(cookieStorage);
    }

    public MordaCleanvarsRequest cleanvars(Morda<?> morda, MordaCleanvarsBlock... blocks) {
        return new MordaCleanvarsRequest(morda, blocks)
                .cookieStorage(cookieStorage);
    }

    public RestAssuredGetRequest morda(Morda<?> morda) {
        List<RequestAction<RestAssuredGetRequest>> actionsBefore = new ArrayList<>();
        actionsBefore.add(setRegionIfNeeded(morda));
        actionsBefore.add(setLanguageIfNeeded(morda));
        actionsBefore.addAll(authIfNeeded(morda));

        RestAssuredGetRequest request = new RestAssuredGetRequest(morda.getUrl())
                .cookieStorage(cookieStorage)
                .beforeRequest(actionsBefore)
                .step("Get " + morda.toString());
        morda.getCookies().entrySet().forEach(e -> request.cookie(e.getKey(), e.getValue()));
        morda.getHeaders().entrySet().forEach(e -> request.header(e.getKey(), e.getValue()));
        return request;
    }

    public MordaGpsaveRequest gpsave(MordaWithRegion morda, int precision, MordaGpsaveDevice device, MordaGpsaveFormat format) {
        final MordaClient mordaClient = this;
        final GeobaseRegion geobaseRegion = morda.getRegion();
        return new MordaGpsaveRequest(morda.getUrl())
                .beforeRequest(RequestAction.requestAction(e -> {
                    GeobaseRegionData regionData = geobaseRegion.getData();
                    e.withSk(mordaClient.cleanvars(morda, "sk").read().getSk())
                            .withLat(regionData.getLatitude())
                            .withLon(regionData.getLongitude())
                            .withLang(morda.getLanguage());
                }))
                .withDevice(device)
                .withFormat(format)
                .cookieStorage(cookieStorage)
                .withPrecision(precision);
    }


    public MordaGpsaveRequest gpsave(URI mordaUri, double lat, double lon, int precision, String sk) {
        return new MordaGpsaveRequest(mordaUri)
                .cookieStorage(cookieStorage)
                .withLat(lat)
                .withLon(lon)
                .withPrecision(precision)
                .withSk(sk);
    }


    public SearchApiClient search() {
        return new SearchApiClient();
    }

    public MordaSetClient set(URI uri) {
        return new MordaSetClient(uri, cookieStorage);
    }

    public RestAssuredGetRequest any(URI anyHost, String environment, URI url) {
        URI anyUrl = UriBuilder.fromUri(anyHost)
                .path(url.getPath())
                .replaceQuery(url.getQuery())
                .build();
        String host = url.getHost();
        RestAssuredGetRequest request = new RestAssuredGetRequest(anyUrl)
                .followRedirects(false);
        if (url.getScheme().equals("https")) {
            request.header("X-YANDEX-HTTPS", "1");
        }
        if (environment.equals("production")) {
            request.header("HOST", host);
        } else {
            request.header("DEV-HOST", host);
        }
        return request;
    }

    public RestAssuredGetRequest weather(String userAgent, URI uri) {
        return new RestAssuredGetRequest(uri)
                .cookieStorage(cookieStorage)
                .header(Morda.USER_AGENT, userAgent)
                .step("Get " + uri.toString());
    }

}
