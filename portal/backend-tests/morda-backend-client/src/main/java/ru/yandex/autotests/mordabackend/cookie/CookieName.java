package ru.yandex.autotests.mordabackend.cookie;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.02.14
 */
public enum CookieName {
    YANDEX_GID("yandex_gid"),
    W("w"),
    YANDEXUID("yandexuid");

    private String name;

    private CookieName(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
