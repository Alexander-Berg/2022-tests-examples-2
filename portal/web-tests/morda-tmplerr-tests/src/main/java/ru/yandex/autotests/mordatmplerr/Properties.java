package ru.yandex.autotests.mordatmplerr;

import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * User: leonsabr
 * Date: 24.10.11
 * Класс со свойствами для профиля .com морды.
 */

@Resource.Classpath("config.properties")
public class Properties extends BaseProperties {
    public Properties() {
        super();
        PropertyLoader.populate(this);
    }

    @Property("android.chrome.ua")
    private String androidChromeUa;

    @Property("iphone.safari.ua")
    private String iphoneSafariUa;

    @Property("iphone.chrome.ua")
    private String iphoneChromeUa;

    @Property("wp.ua")
    private String wpUa;

    @Property("tizen.ua")
    private String tizenUa;

    @Property("tablet.ua")
    private String tabletUa;

    @Property("pda.ua")
    private String pdaUa;

    @Property("fuid01.noexperiment")
    private String fuid01NoExperiment;

    @Property("fuid01.experiment")
    private String fuid01Experiment;

    public String getAndroidChromeUa() {
        return androidChromeUa;
    }

    public String getIphoneSafariUa() {
        return iphoneSafariUa;
    }

    public String getWpUa() {
        return wpUa;
    }

    public String getTizenUa() {
        return tizenUa;
    }

    public String getTabletUa() {
        return tabletUa;
    }

    public String getPdaUa() {
        return pdaUa;
    }

    public String getIphoneChromeUa() {
        return iphoneChromeUa;
    }

    public String getFuid01NoExperiment() {
        return fuid01NoExperiment;
    }

    public String getFuid01Experiment() {
        return fuid01Experiment;
    }
}
