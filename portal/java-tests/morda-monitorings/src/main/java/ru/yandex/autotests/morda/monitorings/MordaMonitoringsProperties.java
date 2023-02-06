package ru.yandex.autotests.morda.monitorings;

import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/05/16
 */
@Resource.Classpath("morda-monitorings.properties")
public class MordaMonitoringsProperties {

    private MordaPagesProperties mordaPagesProperties = new MordaPagesProperties();

    public String getScheme() {
        return mordaPagesProperties.getScheme();
    }

    public String getEnvironment() {
        return mordaPagesProperties.getEnvironment();
    }

    @Property("monitorings.notify")
    private boolean notify = true;

    public boolean toNotify() {
        return notify;
    }


}
