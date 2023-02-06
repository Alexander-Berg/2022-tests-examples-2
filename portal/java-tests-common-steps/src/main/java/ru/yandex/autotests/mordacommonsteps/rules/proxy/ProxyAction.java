package ru.yandex.autotests.mordacommonsteps.rules.proxy;

import net.lightbody.bmp.proxy.ProxyServer;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public interface ProxyAction {
    boolean isNeeded();
    void perform(ProxyServer proxyServer);
}
