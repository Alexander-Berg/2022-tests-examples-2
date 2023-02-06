package ru.yandex.autotests.mainmorda.utils;

/**
 * User: ivannik
 * Date: 05.05.2014
 */
public enum ServiceName {
    AVIA, AUTO, AFISHA, EGE, ZNO, BLOGS, TRAFFIC, TIME, VIDEO, MAPS, YACA, REALTY, MARKET, MUSIC, POGODA, RASP, IMAGES,
    SLOVARI, TAXI, TV, TRANSLATE, NMAPS, SEARCH, RABOTA, NEWS, MONEY, DISK, CALENDAR, MOIKRUG, MAIL, FOTKI, DNS, MASTER,
    WOW, MOBILE, WEBMASTER, PDD, METRIKA, PARTNERS, SITE, CWEBMASTER, AWEBMASTER, XML, SPRAV, DIRECT, STAT, ADVERTISING,
    IE, FX, OPERA, PUNTO, VISUAL, MANAGER, YABROWSER, ELEMENT, LINGVO, INTERNET, COLLECTION, YARU, FAMILY, DZEN,
    ADVANDCED, LARGE, COM, API_JSLIBS, API_MONEY, API_BLOGS, API_SHARE, API_DIRECTOR, API_DIRECT, API_MAPS, API_SPELLER,
    API_FOTKI, WDGT, BROWSER, GAMES, SPORT, ZAKLADKI, NAHODKI, PEOPLE, USLUGI, SOFT, ALL, APPSEARCH, GOROD, NEWSP, FINE,
    TRAVEL, MONEY_SERV, RADIO;

    @Override
    public String toString() {
        return super.toString().toLowerCase();
    }

    public static ServiceName fromString(String id) {
        for (ServiceName serviceName : ServiceName.values()) {
            if (serviceName.toString().equals(id)) {
                return serviceName;
            }
        }
        throw new IllegalArgumentException("May not valid service id: " + id);
    }
}
