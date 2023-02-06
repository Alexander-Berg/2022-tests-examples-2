package ru.yandex.autotests.morda.tests.web.utils;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class GeoCoordinates {
    private final String lat;
    private final String lon;

    public GeoCoordinates(String lat, String lon) {
        this.lat = lat;
        this.lon = lon;
    }

    public String getLat() {
        return lat;
    }

    public String getLon() {
        return lon;
    }
}
