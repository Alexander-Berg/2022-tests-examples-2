package ru.yandex.autotests.tuneapitests;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

/**
 * User: leonsabr
 * Date: 08.06.12
 * Параметры запуска профиля
 */
@Resource.Classpath("tunetests.properties")
public class Properties {
    public Properties() {
        PropertyLoader.populate(this);
    }

    @Property("tune.env")
    private String tuneEnv;

    @Property("tune.protocol")
    private String tuneProtocol;

    @Property("tune.internal.env")
    private String tuneInternalEnv;

    @Property("tune.internal.protocol")
    private String tuneInternalProtocol;

    public String getTuneEnv() {
        return tuneEnv;
    }

    public String getTuneProtocol() {
        return tuneProtocol;
    }

    public String getTuneInternalEnv() {
        return tuneInternalEnv;
    }

    public String getTuneInternalProtocol() {
        return tuneInternalProtocol;
    }
}
