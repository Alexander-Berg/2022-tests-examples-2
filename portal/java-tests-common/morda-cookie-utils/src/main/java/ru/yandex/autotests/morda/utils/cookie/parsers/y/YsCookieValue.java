package ru.yandex.autotests.morda.utils.cookie.parsers.y;

public class YsCookieValue {
    private String cookie;
    private String name;
    private String value;

    public YsCookieValue(String cookie) {
        if (cookie == null || cookie.isEmpty()) {
            throw new IllegalArgumentException("Ys cookie must not be null or empty");
        }

        String[] parts = cookie.split("\\.");
        if (parts.length != 2) {
            throw new IllegalArgumentException("Failed to parse ys value of \"" + cookie + "\"");
        }

        this.cookie = cookie;
        this.name = parts[0];
        this.value = parts[1];
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
