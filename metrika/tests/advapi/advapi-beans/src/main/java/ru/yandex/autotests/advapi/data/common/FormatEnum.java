package ru.yandex.autotests.advapi.data.common;

/**
 * Created by okunev on 18.11.2014.
 */
public enum FormatEnum {

    JSON(".json", "application/json"),
    JAVASCRIPT(null, "application/javascript"),
    CSV(".csv", "application/csv"),
    XLSX(".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");

    private final String format;

    private final String mimeType;

    FormatEnum(String format, String mimeType) {
        this.format = format;
        this.mimeType = mimeType;
    }

    public String getFormat() {
        return format;
    }

    public String getMimeType() {
        return mimeType;
    }

}
