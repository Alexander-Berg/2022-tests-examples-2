package ru.yandex.autotests.morda.api.search;

import ru.yandex.geobase.regions.Countries;
import ru.yandex.geobase.regions.GeobaseRegion;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25/05/16
 */
public enum SearchApiCountry {
    RU("ru", Countries.RUSSIA),
    UA("ua", Countries.UKRAINE),
    KZ("kz", Countries.KAZAKHSTAN),
    BY("by", Countries.BELARUS),
    TR("tr", Countries.TURKEY);

    private String value;
    private GeobaseRegion country;

    SearchApiCountry(String value, GeobaseRegion country) {
        this.value = value;
        this.country = country;
    }

    public static SearchApiCountry forRegion(GeobaseRegion region) {
        for (SearchApiCountry countryCode : SearchApiCountry.values()) {
            if (region.isIn(countryCode.country)) {
                return countryCode;
            }
        }
        return RU;
    }

    public static SearchApiCountry forRegion(int region) {
        return forRegion(new GeobaseRegion(region));
    }

    public String getValue() {
        return value;
    }

    public GeobaseRegion getCountry() {
        return country;
    }
}
