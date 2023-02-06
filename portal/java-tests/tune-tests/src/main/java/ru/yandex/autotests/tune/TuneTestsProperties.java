package ru.yandex.autotests.tune;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * User: asamar
 * Date: 30.11.16
 */
@Resource.Classpath("tune-tests.properties")
public class TuneTestsProperties {

    public TuneTestsProperties() {
        PropertyLoader.populate(this);
    }

    @Property("morda.useragent.touch.iphone")
    private String mordaUserAgentTouchIphone;

    @Property("morda.scheme")
    private String mordaScheme;

    @Property("morda.environment")
    private String mordaEnvironment;

    public String getMordaUserAgentTouchIphone() {
        return mordaUserAgentTouchIphone;
    }

    public String getMordaScheme() {
        return mordaScheme;
    }

    public String getMordaEnvironment() {
        return mordaEnvironment;
    }
}
