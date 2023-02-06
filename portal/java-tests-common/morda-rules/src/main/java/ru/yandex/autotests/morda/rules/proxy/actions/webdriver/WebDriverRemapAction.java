package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.http.BrowserMobHttpRequest;
import ru.yandex.autotests.morda.rules.proxy.actions.RemapAction;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;

import java.net.URI;
import java.util.Map;
import java.util.regex.Pattern;

import static javax.ws.rs.core.UriBuilder.fromUri;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public class WebDriverRemapAction extends RemapAction<MordaBaseWebDriverRule> {

    private WebDriverRemapAction(MordaBaseWebDriverRule rule) {
        super(rule);
        rule.register(this);
    }

    public static WebDriverRemapAction webDriverRemapAction(MordaBaseWebDriverRule rule) {
        return new WebDriverRemapAction(rule);
    }

    @Override
    public void perform() {
        if (isEnabled()) {
            super.perform();
            rule.getProxyServer().addRequestInterceptor((BrowserMobHttpRequest request, Har har) -> {
                URI uri = request.getMethod().getURI();
                String host = request.getMethod().getURI().getHost();

                for (Map.Entry<Pattern, String> entry : remapData.entrySet()) {
                    if (entry.getKey().matcher(host).matches()) {
                        request.getMethod().setURI(fromUri(uri).host(entry.getValue()).build());
                        LOG.info("Remap request from " + host + " to " + entry.getValue());
                        return;
                    }
                }
            });
        }
    }
}
