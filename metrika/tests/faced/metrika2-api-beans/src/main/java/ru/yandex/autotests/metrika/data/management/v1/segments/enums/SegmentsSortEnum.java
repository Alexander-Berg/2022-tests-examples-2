package ru.yandex.autotests.metrika.data.management.v1.segments.enums;

/**
 * Created by konkov on 02.11.2015.
 */
public enum SegmentsSortEnum {

    CREATE_DATE("create_date"),
    WEEK_USERS("week_users"),
    MONTH_USERS("month_users"),
    RETARGETING("retargeting"),
    NAME("name");

    private final String value;

    SegmentsSortEnum(String value) {
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
