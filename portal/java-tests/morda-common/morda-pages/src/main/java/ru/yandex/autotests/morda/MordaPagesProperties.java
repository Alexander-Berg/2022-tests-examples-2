package ru.yandex.autotests.morda;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/05/16
 */
@Resource.Classpath("morda-pages.properties")
public class MordaPagesProperties {

    @Property("morda.scheme")
    private String scheme = "https";

    @Property("morda.environment")
    private String environment = "production";

    @Property("morda.useragent.desktop")
    private String desktopUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:34.0) Gecko/20100101 Firefox/34.0";

    @Property("morda.useragent.touch")
    private String touchUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_0 like Mac OS X) AppleWebKit/601.1.37 " +
            "(KHTML, like Gecko) Version/8.0 Mobile/13A4293g Safari/600.1.4";

    @Property("morda.useragent.touchwp")
    private String touchwpUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 " +
            "(KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53";

    @Property("morda.useragent.pda")
    private String pdaUserAgent = "Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.334; U; id) " +
            "Presto/2.5.25 Version/10.54";

    @Property("morda.useragent.tel")
    private String telUserAgent = "Nokia6300/2.0 (04.20) Profile/MIDP-2.0 Configuration/CLDC-1.1 UNTRUSTED/1.0";

    @Property("morda.useragent.tablet")
    private String tabletUserAgent = "Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 " +
            "(KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4";

    @Property("morda.useragent.smarttv")
    private String smartTvUserAgent = "Mozilla/5.0 (SMART-TV; X11; Linux arm7l) AppleWebkit/537.42 (KHTML, like Gecko) " +
            "Chromium/25.0.1349.2 Chrome/25.0.1349.2 Safari/537.42";

    public MordaPagesProperties() {
        PropertyLoader.populate(this);
    }

    public String getDesktopUserAgent() {
        return desktopUserAgent;
    }

    public String getEnvironment() {
        return environment;
    }

    public String getPdaUserAgent() {
        return pdaUserAgent;
    }

    public String getScheme() {
        return scheme;
    }

    public String getSmartTvUserAgent() {
        return smartTvUserAgent;
    }

    public String getTouchUserAgent() {
        return touchUserAgent;
    }

    public String getTouchwpUserAgent() {
        return touchwpUserAgent;
    }

    public String getTelUserAgent() {
        return telUserAgent;
    }

    public String getTabletUserAgent() {
        return tabletUserAgent;
    }
}
