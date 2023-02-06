package ru.yandex.autotests.morda.api;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.MordaWithLanguage;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.autotests.morda.restassured.requests.Request;
import ru.yandex.autotests.morda.restassured.requests.Request.RequestAction;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredPostRequest;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.usermanager.beans.UserData;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.morda.restassured.requests.Request.RequestAction.requestAction;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 09/08/16
 */
public class MordaRequestActions {
    private static final Logger LOGGER = Logger.getLogger(MordaRequestActions.class);

    public static <T extends Request<T>> RequestAction<T> setRegion(GeobaseRegion region) {
        if (region == null) {
            return RequestAction.empty();
        }
        return requestAction((request) -> {
//            LOGGER.info("Set region " + region + " with cookie yandex_gid=" + region.getRegionId());
            request.cookie("yandex_gid", String.valueOf(region.getRegionId()));
        });
    }

    public static <T extends Request<T>> RequestAction<T> setLanguage(MordaLanguage language) {
        if (language == null) {
            return RequestAction.empty();
        }
        return requestAction((request) -> {
            String currentMy = request.getCookieStorage() != null
                    ? request.getCookieStorage().getCookies().get("my")
                    : "";
            String newMy = language.setLanguageInMyCookie(currentMy);
//            LOGGER.info("Set language " + language + " with cookie my=" + newMy);
            request.cookie("my", newMy);
        });
    }

    public static <T extends Request<T>> RequestAction<T> auth(Morda<?> morda, UserData user) {
        URI passportUri = UriBuilder.fromUri(morda.getPassportHost()).path("passport").build();
        return requestAction((request) -> {
//            LOGGER.info("Login as " + user.getLogin() + ":" + user.getPassword());
            String postData = "login=" + user.getLogin() + "&passwd=" + user.getPassword();

            new RestAssuredPostRequest<String>(passportUri)
                    .contentType("application/x-www-form-urlencoded")
                    .post(postData)
                    .cookieStorage(request.getCookieStorage())
                    .readAsResponse();
        });
    }

    public static <T extends Request<T>> List<RequestAction<T>> authIfNeeded(Morda<?> morda) {
        List<RequestAction<T>> result = new ArrayList<>();
        morda.getUsers().forEach(e -> result.add(auth(morda, e)));
        return result;
    }

    public static <T extends Request<T>> RequestAction<T> setRegionIfNeeded(Morda<?> morda) {
        if (morda instanceof MordaWithRegion) {
            GeobaseRegion region = ((MordaWithRegion) morda).getRegion();
            return setRegion(region);
        }
        return requestAction(request -> {
        });
    }

    public static <T extends Request<T>> RequestAction<T> setLanguageIfNeeded(Morda<?> morda) {
        if (morda instanceof MordaWithLanguage) {
            return setLanguage(morda.getLanguage());
        }
        return requestAction(request -> {
        });
    }

    public static <T extends Request<T>> T prepareRequest(T request, Morda<?> morda) {
        if (morda == null) {
            return request;
        }

        request.beforeRequest(setRegionIfNeeded(morda));
        request.beforeRequest(setLanguageIfNeeded(morda));
        request.beforeRequest(authIfNeeded(morda));

        morda.getCookies().forEach(request::cookie);
        morda.getHeaders().forEach(request::header);

        return request;
    }
}
