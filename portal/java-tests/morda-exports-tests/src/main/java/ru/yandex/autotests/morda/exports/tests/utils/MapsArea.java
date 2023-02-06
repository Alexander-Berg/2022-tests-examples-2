package ru.yandex.autotests.morda.exports.tests.utils;

import org.apache.commons.lang.builder.EqualsBuilder;
import org.apache.commons.lang.builder.HashCodeBuilder;
import org.apache.commons.lang.builder.ToStringBuilder;
import org.apache.commons.lang.builder.ToStringStyle;

public class MapsArea {
    private double lon;
    private double lat;
    private double spnlon;
    private double spnlat;

    private MapsArea(double lon, double lat, double spnlon, double spnlat) {
        this.lon = lon;
        this.lat = lat;
        this.spnlon = spnlon;
        this.spnlat = spnlat;
    }

    public static MapsArea createMapsArea(double lon, double lat, double spnlon, double spnlat) {
        MapsArea area = new MapsArea(lon, lat, spnlon, spnlat);

        if (spnlat == 0 || spnlon == 0) {
            throw new RuntimeException("spnlon or spnlat equals 0: " + area);
        }

        return area;
    }

    public static MapsArea createMapsArea(String lonStr, String latStr, double spnlon, double spnlat) {
        Double lon = Double.parseDouble(lonStr);
        Double lat = Double.parseDouble(latStr);

        return createMapsArea(lon, lat, spnlon, spnlat);
    }

    public static MapsArea createMapsArea(String lonStr, String latStr, String spnlonStr, String spnlatStr) {
        Double lon = Double.parseDouble(lonStr);
        Double lat = Double.parseDouble(latStr);
        Double spnlon = Double.parseDouble(spnlonStr);
        Double spnlat = Double.parseDouble(spnlatStr);

        return createMapsArea(lon, lat, spnlon, spnlat);
    }

    public boolean intersects(MapsArea mapsArea) {
        double x1 = Math.max(lon - spnlon, mapsArea.lon - mapsArea.spnlon);
        double y1 = Math.max(lat - spnlat, mapsArea.lat - mapsArea.spnlat);

        double x2 = Math.min(lon + spnlon, mapsArea.lon + mapsArea.spnlon);
        double y2 = Math.min(lat + spnlat, mapsArea.lat + mapsArea.spnlat);

        return x1 < x2 && y1 < y2;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this, ToStringStyle.SHORT_PREFIX_STYLE);
    }

    @Override
    public boolean equals(Object that) {
        return EqualsBuilder.reflectionEquals(this, that);
    }

    @Override
    public int hashCode() {
        return HashCodeBuilder.reflectionHashCode(this);
    }
}