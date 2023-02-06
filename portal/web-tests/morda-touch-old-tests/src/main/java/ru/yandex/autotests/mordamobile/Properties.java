package ru.yandex.autotests.mordamobile;


import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;


/**
 * User: alex89
 * Date: 12.09.12
 */
@Resource.Classpath("config.properties")
public class Properties extends BaseProperties {
    public Properties() {
        super();
        PropertyLoader.populate(this);
    }

    @Property("user.agent")
    private String userAgent;

    public String getUserAgent() {
        return userAgent;
    }
}
