package ru.yandex.autotests.mordabackend.cookie;

import java.io.Serializable;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */
public class Cookie implements Serializable {
    private String name;
    private String value;

    public Cookie(CookieName name, String value) {
        this.name = name.getName();
        this.value = value;
    }

    public Cookie(String name, String value) {
        this.name = name;
        this.value = value;
    }

    @Override
    public String toString() {
        return name + "=" + value;
    }

    public String getName() {
        return name;
    }

    public String getValue() {
        return value;
    }
}
