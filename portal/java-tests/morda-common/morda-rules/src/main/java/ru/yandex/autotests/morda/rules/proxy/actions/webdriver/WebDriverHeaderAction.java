package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.autotests.morda.rules.proxy.actions.HeaderAction;

import java.util.Map;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public class WebDriverHeaderAction extends HeaderAction<MordaBaseWebDriverRule> {

    public WebDriverHeaderAction(MordaBaseWebDriverRule rule) {
        super(rule);
        rule.register(this);
    }

    public static WebDriverHeaderAction webDriverHeaderAction(MordaBaseWebDriverRule rule) {
        return new WebDriverHeaderAction(rule);
    }

    @Override
    public void perform() {
        super.populateFromProperties();
        if (isEnabled()) {
            super.perform();
            rule.getProxyServer().addRequestFilter((httpRequest, httpMessageContents, httpMessageInfo) -> {

                for (Map.Entry<String, String> header : headers.entrySet()) {
                    httpRequest.headers().remove(header.getKey());
                    httpRequest.headers().add(header.getKey(), header.getValue());
                }

                return null;
            });


        }
    }
}
