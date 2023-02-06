package ru.yandex.autotests.metrika.data.report.v1.enums;

/**
 * Created by sourx on 20/06/16.
 */
public enum ReportFilterType {
    METRIKA("AND", "OR", "(%s %s %s)"),
    ANALYTICS(";", ",", "%s%s%s");

    private final String and;

    private final String or;

    private final String format;

    ReportFilterType(String and, String or, String format) {
        this.and = and;
        this.or = or;
        this.format = format;
    }

    public String getAnd() {
        return and;
    }

    public String getOr() {
        return or;
    }

    public String getFormat() {
        return format;
    }
}
