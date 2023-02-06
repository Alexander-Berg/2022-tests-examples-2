package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

import net.lightbody.bmp.proxy.ProxyServer;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ConfigProxyAction;

import java.util.ArrayList;
import java.util.List;

public class BlacklistAction
        extends ConfigProxyAction<List<String>>
        implements MergeableProxyAction<List<String>>, ReplaceableProxyAction<List<String>> {

    private static final Logger LOG = Logger.getLogger(BlacklistAction.class);
    private static final Properties CONFIG = new Properties();

    private BlacklistAction() {
        super(new ArrayList<>(CONFIG.getBlackList()));
    }

    @Override
    public boolean isNeeded() {
        return !data.isEmpty();
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        LOG.info("Added blacklist patterns: " + data);
        for (String request : data) {
            proxyServer.blacklistRequests(request, 200);
        }
    }

    @Override
    public void mergeWith(List<String> data) {
        this.data.addAll(data);
    }

    @Override
    public void replaceWith(List<String> data) {
        this.data = data;
    }

    static BlacklistAction blackList() {
        return new BlacklistAction();
    }
}
