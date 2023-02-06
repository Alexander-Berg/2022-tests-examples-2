package ru.yandex.autotests.morda.api.search;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.geobase.regions.GeobaseRegion;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 03/10/16
 */
public class SearchApiRequestData {

    private SearchApiVersion version;
    private SearchApiBlock block = SearchApiBlock.ALL;
    private GeobaseRegion geo;
    private SearchApiCountry country;
    private GeobaseRegion geoForCoords;
    private double lat;
    private double lon;
    private MordaLanguage language;
    private SearchApiDp dp;
    private String oauth;
    private String appVersion;

    public SearchApiBlock getBlock() {
        return block;
    }

    public SearchApiRequestData setBlock(SearchApiBlock block) {
        this.block = block;
        return this;
    }

    public SearchApiVersion getVersion() {
        return version;
    }

    public SearchApiRequestData setVersion(SearchApiVersion version) {
        this.version = version;
        return this;
    }

    public GeobaseRegion getGeo() {
        return geo;
    }

    public SearchApiRequestData setGeo(GeobaseRegion geo) {
        this.geo = geo;
        return this;
    }

    public SearchApiCountry getCountry() {
        return country;
    }

    public SearchApiRequestData setCountry(SearchApiCountry country) {
        this.country = country;
        return this;
    }

    public GeobaseRegion getGeoForCoords() {
        return geoForCoords;
    }

    public SearchApiRequestData setGeoForCoords(GeobaseRegion geoForCoords) {
        this.geoForCoords = geoForCoords;
        return this;
    }

    public MordaLanguage getLanguage() {
        return language;
    }

    public SearchApiRequestData setLanguage(MordaLanguage language) {
        this.language = language;
        return this;
    }

    public SearchApiDp getDp() {
        return dp;
    }

    public SearchApiRequestData setDp(SearchApiDp dp) {
        this.dp = dp;
        return this;
    }

    public String getOauth() {
        return oauth;
    }

    public SearchApiRequestData setOauth(String oauth) {
        this.oauth = oauth;
        return this;
    }

    public double getLat() {
        return lat;
    }

    public SearchApiRequestData setLat(double lat) {
        this.lat = lat;
        return this;
    }

    public double getLon() {
        return lon;
    }

    public SearchApiRequestData setLon(double lon) {
        this.lon = lon;
        return this;
    }

    public String getAppVersion() {
        return appVersion;
    }

    public SearchApiRequestData setAppVersion(String appVersion) {
        this.appVersion = appVersion;
        return this;
    }

    @Override
    public String toString() {
        if (version != null) {
            return version.name() + ", geo=" + getGeo() + ", lang=" + getLanguage();
        }
        return "geo=" + getGeo() + ", lang=" + getLanguage();
    }
}
