package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

import net.lightbody.bmp.proxy.ProxyServer;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ConfigProxyAction;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public final class UserAgentAction extends ConfigProxyAction<String>
        implements ReplaceableProxyAction<String> {

    private static final Properties CONFIG = new Properties();
    private static final Logger LOG = Logger.getLogger(UserAgentAction.class);
    private static final String USER_AGENT = "User-Agent";

    private UserAgentAction() {
        super(CONFIG.getUserAgent());
    }

    @Override
    public boolean isNeeded() {
        return data != null;
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        proxyServer.addHeader(USER_AGENT, data);
        LOG.info("Added User-Agent: " + data);
    }

    @Override
    public void replaceWith(String data) {
        this.data = data;
    }

    static UserAgentAction userAgent() {
        return new UserAgentAction();
    }
}
