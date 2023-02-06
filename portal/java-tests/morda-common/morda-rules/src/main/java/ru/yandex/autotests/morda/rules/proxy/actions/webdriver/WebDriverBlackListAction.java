package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import ru.yandex.autotests.morda.rules.proxy.actions.BlacklistAction;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;

/**
 * User: asamar
 * Date: 09.09.2015.
 */
public class WebDriverBlackListAction extends BlacklistAction<MordaBaseWebDriverRule> {


    private WebDriverBlackListAction(MordaBaseWebDriverRule browserRule) {
        super(browserRule);
        rule.register(this);
    }

    public static WebDriverBlackListAction webDriverBlackListAction(MordaBaseWebDriverRule rule) {
        return new WebDriverBlackListAction(rule);
    }

    @Override
    public void perform() {
        if (!isEnabled()) {
            return;
        }
        super.perform();
        patterns.forEach(request -> rule.getProxyServer().blacklistRequests(request, 200));
    }

}
