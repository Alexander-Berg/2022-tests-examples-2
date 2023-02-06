package ru.yandex.autotests.mordatmplerr.mordatypes;

import org.openqa.selenium.remote.DesiredCapabilities;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21.03.14
 */
public enum Browser {
    FIREFOX(DesiredCapabilities.firefox()),
    CHROME(DesiredCapabilities.chrome());
//    IE(DesiredCapabilities.internetExplorer());

    private DesiredCapabilities caps;

    private Browser(DesiredCapabilities caps) {
        this.caps = caps;
    }

    public DesiredCapabilities getCaps() {
        return new DesiredCapabilities(caps);
    }
}
