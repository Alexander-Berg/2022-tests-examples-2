package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

import net.lightbody.bmp.proxy.ProxyServer;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ConfigProxyAction;

import java.util.Set;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public class HeaderAction extends ConfigProxyAction<Set<Header>>
        implements MergeableProxyAction<Set<Header>>, ReplaceableProxyAction<Set<Header>> {
    private static final Properties CONFIG = new Properties();
    private static final Logger LOG = Logger.getLogger(HeaderAction.class);

    public HeaderAction() {
        super(CONFIG.getHeaders());
    }

    @Override
    public boolean isNeeded() {
        return !data.isEmpty();
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        proxyServer.setCaptureHeaders(true);
        for (Header header : data) {
            proxyServer.addHeader(header.getName(), header.getValue());
            LOG.info("Added header: " + header);
        }
    }

    @Override
    public void mergeWith(Set<Header> data) {
        this.data.addAll(data);
    }

    @Override
    public void replaceWith(Set<Header> data) {
        this.data = data;
    }

    static HeaderAction headers() {
        return new HeaderAction();
    }
}
