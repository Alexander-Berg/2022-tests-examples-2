package ru.yandex.autotests.mordacommonsteps.rules.proxy.actions;

import net.lightbody.bmp.proxy.ProxyServer;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ProxyAction;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public class HarAction implements ProxyAction {
    private static final Logger LOG = Logger.getLogger(HarAction.class);
    private String name;

    public HarAction(String name) {
        this.name = name;
    }

    @Override
    public boolean isNeeded() {
        return true;
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        proxyServer.newHar(name);
        LOG.info("Added har " + name);
    }

    public static ProxyAction addHar(String name) {
        return new HarAction(name);
    }
}
