package ru.yandex.autotests.mainmorda.utils;

/**
 * User: ivannik
 * Date: 12.07.13
 * Time: 18:22
 */
public enum WidgetPatternParameter {
    PROTOTYPE("prototype"),
    WAUTH("wauth"),
    PSETTINGS("psettings"),
    PINNED("pinned"),
    HIDEPROMO("hidePromo"),
    COLUMNSCOUNT("columnsCount"),
    FAKE("fake"),
    LAYOUTTYPE("layoutType"),
    REMOVED("removed"),
    DEFSKIN("defskin"),
    YU("yu");

    public String name;

    private WidgetPatternParameter(String name) {
        this.name = name;
    }

    public static WidgetPatternParameter getParameter(String name) {
        for (WidgetPatternParameter parameter : WidgetPatternParameter.values()) {
            if (parameter.name.equals(name)) {
                return parameter;
            }
        }
        throw new IllegalArgumentException("Parameter " + name + " not exists");
    }

    @Override
    public String toString() {
        return name;
    }
}
