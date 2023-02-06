package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26.05.14
 */
public class Cookie {
    private String name;
    private String value;

    public Cookie(String name, String value) {
        this.name = name;
        this.value = value;
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
        return "<" + name + "=" + value + ">";
    }
}
