package ru.yandex.autotests.internalapid.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

@Resource.Classpath("tvm.properties")
public class TvmProperties {
    private static TvmProperties instance;

    private TvmProperties() {
        PropertyLoader.populate(this);
    }

    public static TvmProperties getInstance() {
        if (instance == null) {
            instance = new TvmProperties();
        }
        return instance;
    }

    @Property("secret.environment")
    private String environment;

    @Property("secret.key")
    private String key;

    @Property("tvm.clientId")
    private int clientId;

    public String getEnvironment() {
        return environment;
    }

    public String getKey() {
        return key;
    }

    public int getClientId() {
        return clientId;
    }
}

