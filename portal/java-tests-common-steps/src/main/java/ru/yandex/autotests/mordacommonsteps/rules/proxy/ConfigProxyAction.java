package ru.yandex.autotests.mordacommonsteps.rules.proxy;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public abstract class ConfigProxyAction<T> implements ProxyAction {
    protected T data;

    protected ConfigProxyAction(T data) {
        this.data = data;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }
}
