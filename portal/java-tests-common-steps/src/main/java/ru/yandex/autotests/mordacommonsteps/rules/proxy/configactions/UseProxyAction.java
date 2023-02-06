package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

import net.lightbody.bmp.proxy.ProxyServer;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ConfigProxyAction;

public class UseProxyAction extends ConfigProxyAction<Boolean> {

    private static final Logger LOG = Logger.getLogger(UseProxyAction.class);
    private static final Properties CONFIG = new Properties();

    private UseProxyAction() {
        super(CONFIG.isUseProxy());
    }

    @Override
    public boolean isNeeded() {
        return data;
    }

    @Override
    public void perform(ProxyServer proxyServer) {
    }

    static UseProxyAction useProxy() {
        return new UseProxyAction();
    }
}
