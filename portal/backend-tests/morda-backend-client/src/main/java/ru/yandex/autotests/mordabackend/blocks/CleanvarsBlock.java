package ru.yandex.autotests.mordabackend.blocks;

/**
 * User: ivannik
 * Date: 06.08.2014
 */
public enum CleanvarsBlock {
    AFISHA("Afisha"),
    AEROEXPRESS("Aeroexpress"),
    APPLICATION("Application"),
    ALERT("Alert"),
    BRIDGES("bridges"),
    REQUESTID("Requestid"),
    BROWSERDESC("BrowserDesc"),
    ISHOLIDAY("IsHoliday"),
    DIRECT("Direct"),
    DISASTER("Disaster"),
    DEVICE_PLATFORM("DevicePlatform"),
    MORDA_CONTENT("MordaContent"),
    MORDA_ZONE("MordaZone"),
    METRO("Metro"),
    ETRAINS("Etrains"),
    GEO("Geo"),
    GEODETECTION("GeoDetection"),
    GEOID("GeoID"),
    GEOLOCATION("GeoLocation"),
    HARITA("Harita"),
    TOPNEWS("Topnews"),
    WRONGDATEALERT("WrongDateAlert"),
    WRONGDATEFATAL("WrongDateFatal"),
    THEMES("Themes"),
    SK("sk"),
    SKIN("Skin"),
    HOMEPAGENOARGS("HomePageNoArgs"),
    YANDEXUID("Yandexuid"),
    WPWAUTH("WPWauth"),
    SKINSETENABLED("SkinSetEnabled"),
    SKINSENABLED("SkinsEnabled"),
    WPSETTINGS("WPSettings"),
    RANDOMSKIN("randomSkin"),
    SKINSCATALOG("SkinsCatalog"),
    DEFSKINARG("DefskinArg"),
    FOOTBALL_TR("football_tr"),
    POI("poi"),
    POI_GROUPS("PoiGroups"),
    POI_FAVOURITE("PoiFavourite"),
    RASP("Rasp"),
    SEARCH("Search"),
    SEARCHURL("SearchUrl"),
    SERVICES_MOBILE("Services_mobile"),
    SERVICES_TABS("Services_tabs"),
    SERVICES("Services"),
    CITY_SUGGEST("citySuggest"),
    STOCKS("Stocks"),
    TRAFFIC("Traffic"),
    TV("TV"),
    LOCAL("Local"),
    LOCAL_DAY_TIME("LocalDayTime"),
    HIDDENTIME("HiddenTime"),
    YYYYMMDD("YYYYMMDD"),
    WEATHER("Weather"),
    WSTEMP("WSTemp"),
    LOGO("Logo"),
    MAIL("Mail"),
    MAILINFO("MailInfo"),
    MINISERVICES("Miniservices"),
    LANGUAGE("Language"),
    LANGUAGE_LC("Language_lc"),
    LANGUAGECHOOSERINFOOTER("LanguageChooserInFooter"),
    SMARTEXAMPLE("SmartExample"),
    BLOCKS("blocks"),
    SET_START_PAGE_LINK("set_start_page_link"),
    WITHOUT_BANNER_DEBUG("(?!Banner_debug).*");

    private String blockName;

    CleanvarsBlock(String blockName) {
        this.blockName = blockName;
    }

    @Override
    public String toString() {
        return blockName;
    }
}
