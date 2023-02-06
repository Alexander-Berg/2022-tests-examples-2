package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

import ru.yandex.autotests.mordacommonsteps.rules.proxy.ConfigProxyAction;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ProxyAction;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import static ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.BlacklistAction.blackList;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.CookieAction.cookies;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction.headers;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.RemapAction.remap;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UseProxyAction.useProxy;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction.userAgent;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26.05.14
 */
public class ConfigProxyActions {
    private Map<Class<? extends ConfigProxyAction>, ConfigProxyAction> proxyActionMap;

    public ConfigProxyActions() {
        this.proxyActionMap = new HashMap<>();
        init();
    }

    private void init() {
        addProxyAction(BlacklistAction.class, blackList());
        addProxyAction(UserAgentAction.class, userAgent());
        addProxyAction(CookieAction.class, cookies());
        addProxyAction(RemapAction.class, remap());
        addProxyAction(HeaderAction.class, headers());
        addProxyAction(UseProxyAction.class, useProxy());
    }

    public <T> void mergeWith(Class<? extends MergeableProxyAction<T>> clazz, T data) {
        MergeableProxyAction<T> configProxyAction =
                (MergeableProxyAction<T>) proxyActionMap.get(clazz);
        configProxyAction.mergeWith(data);
    }

    public <T> void replaceWith(Class<? extends ReplaceableProxyAction<T>> clazz, T data) {
        ReplaceableProxyAction<T> configProxyAction =
                (ReplaceableProxyAction<T>) proxyActionMap.get(clazz);
        configProxyAction.replaceWith(data);
    }

    public void addProxyAction(Class<? extends ConfigProxyAction> clazz, ConfigProxyAction proxyAction) {
        proxyActionMap.put(clazz, proxyAction);
    }

    public void deleteProxyAction(Class<? extends ConfigProxyAction> proxyAction) {
        proxyActionMap.remove(proxyAction);
    }

    public Collection<? extends ProxyAction> getProxyActions() {
        return proxyActionMap.values();
    }
}
