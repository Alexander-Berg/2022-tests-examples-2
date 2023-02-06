package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import net.lightbody.bmp.core.har.Har;
import ru.yandex.autotests.morda.rules.proxy.actions.HarAction;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public class WebDriverHarAction extends HarAction<MordaBaseWebDriverRule> {

    public WebDriverHarAction(MordaBaseWebDriverRule rule) {
        super(rule);
        rule.register(this);
        disable();
    }

    public static WebDriverHarAction webDriverHarAction(MordaBaseWebDriverRule rule) {
        return new WebDriverHarAction(rule);
    }

    @Override
    public MordaBaseWebDriverRule record() {
        enable();
        return rule;
    }

    @Override
    public Har get() {
        return rule.getProxyServer().getHar();
    }

    @Override
    public void perform() {
        if (isEnabled()) {
            super.perform();
            rule.getProxyServer().newHar("har");
        }
    }

}
