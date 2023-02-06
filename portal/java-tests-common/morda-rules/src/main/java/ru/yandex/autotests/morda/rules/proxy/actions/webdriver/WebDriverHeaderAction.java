package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import ru.yandex.autotests.morda.rules.proxy.actions.HeaderAction;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;

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
        if (isEnabled()) {
            super.perform();
            for (Map.Entry<String, String> header : headers.entrySet()) {
                rule.getProxyServer().addHeader(header.getKey(), header.getValue());
            }
        }
    }
}
