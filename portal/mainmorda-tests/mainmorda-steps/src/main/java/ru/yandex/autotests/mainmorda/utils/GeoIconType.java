package ru.yandex.autotests.mainmorda.utils;

/**
 * User: ivannik
 * Date: 05.06.13
 * Time: 13:42
 */
public enum GeoIconType {
    METRO_SPB, METRO_MSK, METRO_KIEV, METRO_HRK, TAXI, PANORAMS, ROUTES, TRAFFIC, RASP,
    ATM, CAFE, DRUGSTORE, BANK, MOVIE, GAZ,
    RANDOM;

    @Override
    public String toString() {
        return super.toString().toLowerCase();
    }
}
