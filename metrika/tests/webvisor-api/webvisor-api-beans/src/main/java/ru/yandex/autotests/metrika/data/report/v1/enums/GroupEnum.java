package ru.yandex.autotests.metrika.data.report.v1.enums;

/**
 * Created by konkov on 05.08.2014.
 */
public enum GroupEnum {

    ALL("all"),
    YEAR("year"),
    QUARTER("quarter"),
    MONTH("month"),
    WEEK("week"),
    DAY("day"),
    HOUR("hour"),
    DEKAMINUTE("dekaminute"),
    MINUTE("minute"),
    AUTO("auto");

    private final String value;

    public static final String parameter = "<group>";

    GroupEnum(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return getValue();
    }

}
