package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.autotests.morda.rules.proxy.actions.RemapAction;

import java.net.URI;
import java.util.Map;
import java.util.regex.Pattern;

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
    public boolean isEnabled() {
        return true;
    }

    @Override
    public void perform() {
        if (isEnabled()) {
            super.perform();

            rule.getProxyServer().addRequestFilter((request, contents, messageInfo) -> {
                String host = URI.create(messageInfo.getUrl()).getHost();
                for (Map.Entry<Pattern, String> entry : remapData.entrySet()) {
                    if (entry.getKey().matcher(host).matches()) {
                        LOG.info("Remapping " + messageInfo.getUrl() + " to " + entry.getValue());
                        rule.getProxyServer().getHostNameResolver().remapHost(host, entry.getValue());
                        return null;
                    }
                }
                return null;
            });
        }
    }
}
