package ru.yandex.autotests.mainmorda;

import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * User: alex89
 * Date: 04.10.12
 */
@Resource.Classpath("config.properties")
public class Properties extends BaseProperties {
    public Properties() {
        super();
        PropertyLoader.populate(this);
    }

    public Mode getMode() {
        return Mode.valueOf(mode.toUpperCase());
    }

    public String getBrowserName() {
        return browserName;
    }

    @Property("mode")
    private String mode = "plain";

    @Property("browser.name")
    private String browserName;
}
