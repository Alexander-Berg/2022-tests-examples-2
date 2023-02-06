package ru.yandex.autotests.morda.api.search;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.restassured.requests.GetRequest;
import ru.yandex.geobase.regions.GeobaseRegion;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 03/10/16
 */
public interface SearchApiRequest<T extends GetRequest<T>> extends GetRequest<T> {

    SearchApiRequestData getRequestData();

    default T populateFromRequestData(SearchApiRequestData requestData) {
        withGeo(requestData.getGeo());
        withCountry(requestData.getCountry());
        if (requestData.getGeoForCoords() != null) {
            withCoords(requestData.getLat(), requestData.getLon());
        }
        withLanguage(requestData.getLanguage());
        withDp(requestData.getDp());
        withOauth(requestData.getOauth());
        return me();
    }

    default T withGeo(int geoId) {
        if (geoId != 0) {
            queryParam("geo", geoId);
            withCountry(SearchApiCountry.forRegion(geoId));
        }
        return me();
    }

    default T withCountry(SearchApiCountry countryCode) {
        if (countryCode != null) {
            queryParam("country", countryCode.getValue());
        }
        return me();
    }

    default T withGeo(GeobaseRegion region) {
        if (region != null) {
            return withGeo(region.getRegionId());
        }
        return me();
    }

    default T withLanguage(String language) {
        if (language != null) {
            queryParam("lang", language);
        }
        return me();
    }

    default T withCoords(double lat, double lon) {
        queryParam("lat", lat);
        queryParam("lon", lon);
        return me();
    }

    default T withCoords(GeobaseRegion region) {
        if (region != null) {
            return withCoords(region.getData().getLatitude(), region.getData().getLongitude());
        }
        return me();
    }

    default T withLanguage(MordaLanguage language) {
        if (language != null) {
            return withLanguage(language.getValue());
        }
        return me();
    }

    default T withDp(String dp) {
        if (dp != null) {
            queryParam("dp", dp);
        }
        return me();
    }

    default T withDp(SearchApiDp dp) {
        if (dp != null) {
            return withDp(dp.getValue());
        }
        return me();
    }

    default T withOauth(String oauth) {
        if (oauth != null) {
            queryParam("oauth", oauth);
        }
        return me();
    }
}
