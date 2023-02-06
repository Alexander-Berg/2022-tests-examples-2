package ru.yandex.autotests.morda.utils.cookie.parsers.y;

public class YpCookieValue {
    private String cookie;
    private String ts;
    private String name;
    private String value;

    public YpCookieValue(String cookie) {
        if (cookie == null || cookie.isEmpty()) {
            throw new IllegalArgumentException("Yp cookie must not be null or empty");
        }

        String[] parts = cookie.split("\\.");
        if (parts.length != 3) {
            throw new IllegalArgumentException("Failed to parse yp value of \"" + cookie + "\"");
        }

        this.cookie = cookie;
        this.ts = parts[0];
        this.name = parts[1];
        this.value = parts[2];
    }

    public String getTs() {
        return ts;
    }

    public void setTs(String ts) {
        this.ts = ts;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return cookie;
    }

}
