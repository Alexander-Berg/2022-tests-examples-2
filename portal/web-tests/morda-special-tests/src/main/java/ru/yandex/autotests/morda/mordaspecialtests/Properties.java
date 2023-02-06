package ru.yandex.autotests.morda.mordaspecialtests;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

@Resource.Classpath("config.properties")
public class Properties {
    public Properties() {
        PropertyLoader.populate(this);
    }

    @Property("timeout")
    private long timeout = 3000;

    @Property("rc")
    private boolean rc = false;

    public long getTimeout() {
        return timeout;
    }

    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }

    public boolean isRc() {
        return rc;
    }

    public void setRc(boolean rc) {
        this.rc = rc;
    }
}
