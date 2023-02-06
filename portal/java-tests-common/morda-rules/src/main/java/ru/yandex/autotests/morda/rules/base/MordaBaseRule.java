package ru.yandex.autotests.morda.rules.base;

import org.openqa.selenium.remote.DesiredCapabilities;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/09/15
 */
public abstract class MordaBaseRule {

    public static MordaBaseWebDriverRule webDriver() {
        return MordaBaseWebDriverRule.webDriverRule();
    }

    public static MordaBaseWebDriverRule webDriver(DesiredCapabilities caps) {
        return MordaBaseWebDriverRule.webDriverRule(caps);
    }
}
