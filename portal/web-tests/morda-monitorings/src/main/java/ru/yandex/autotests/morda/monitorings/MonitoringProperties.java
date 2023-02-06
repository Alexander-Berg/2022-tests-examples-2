package ru.yandex.autotests.morda.monitorings;

import org.apache.commons.beanutils.ConvertUtils;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/05/15
 */
@Resource.Classpath("morda-monitorings.properties")
public class MonitoringProperties extends BaseProperties {
    public MonitoringProperties() {
        ConvertUtils.register(new ListConverter(", "), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    @Property("morda.useragent.touch.iphone")
    private String mordaUserAgentTouchIphone;

    @Property("morda.useragent.smarttv")
    private String smartTvUserAgent = "Mozilla/5.0 (SMART-TV; X11; Linux arm7l) AppleWebkit/537.42 (KHTML, like Gecko) " +
            "Chromium/25.0.1349.2 Chrome/25.0.1349.2 Safari/537.42";

    @Property("morda.scheme")
    private String mordaScheme;

    @Property("morda.environment")
    private String mordaEnvironment;

    public String getMordaUserAgentTouchIphone() {
        return mordaUserAgentTouchIphone;
    }

    public String getSmartTvUserAgent() {
        return smartTvUserAgent;
    }

    public String getMordaScheme() {
        return mordaScheme;
    }

    public String getMordaEnvironment() {
        return mordaEnvironment;
    }
}
