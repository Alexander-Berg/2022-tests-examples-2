package ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.ProxyServer;
import net.lightbody.bmp.proxy.http.BrowserMobHttpRequest;
import net.lightbody.bmp.proxy.http.RequestInterceptor;
import org.apache.log4j.Logger;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ConfigProxyAction;

import java.net.URI;
import java.util.Map;
import java.util.regex.Pattern;

import static javax.ws.rs.core.UriBuilder.fromUri;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.01.14
 */
public class RemapAction extends ConfigProxyAction<Map<Pattern, String>>
        implements MergeableProxyAction<Map<Pattern, String>>, ReplaceableProxyAction<Map<Pattern, String>> {
    private static final Properties CONFIG = new Properties();
    private static final Logger LOG = Logger.getLogger(RemapAction.class);

    private RemapAction() {
        super(CONFIG.getRemap());
    }

    @Override
    public boolean isNeeded() {
        return !data.isEmpty();
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        proxyServer.addRequestInterceptor(new RequestInterceptor() {
            @Override
            public void process(BrowserMobHttpRequest request, Har har) {
                URI uri = request.getMethod().getURI();
                String host = request.getMethod().getURI().getHost();
                for (Map.Entry<Pattern, String> entry : data.entrySet()) {
                    if (entry.getKey().matcher(host).matches()) {
                        request.getMethod().setURI(fromUri(uri).host(entry.getValue()).build());
                        LOG.info("Added host remap for " + host + " to " + entry.getValue());
                        return;
                    }
                }
            }
        });
    }

    static RemapAction remap() {
        return new RemapAction();
    }

    @Override
    public void mergeWith(Map<Pattern, String> data) {
        this.data.putAll(data);
    }

    @Override
    public void replaceWith(Map<Pattern, String> data) {
        this.data = data;
    }
}
