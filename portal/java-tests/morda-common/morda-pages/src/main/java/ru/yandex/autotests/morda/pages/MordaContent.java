package ru.yandex.autotests.morda.pages;

public enum MordaContent {
    ALL("all"),
    BIG("big"),
    HW("hw"),
    COM("com"),
    COMTR("comtr"),
    COMTRFOOT("comtrfoot"),
    FAMILY("family"),
    FIREFOX("firefox"),
    TOUCH("touch"),
    MOB("mob"),
    TEL("tel"),
    TABLET("tablet"),
    OPANEL("opanel"),
    YARU("yaru"),
    SEARCH_API("search_api"),
    TV("tv"),
    TUNE("tune");

    private String value;

    MordaContent(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
