package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26.05.14
 */
public interface MergeableProxyAction<T> {
    public void mergeWith(T data);
}
