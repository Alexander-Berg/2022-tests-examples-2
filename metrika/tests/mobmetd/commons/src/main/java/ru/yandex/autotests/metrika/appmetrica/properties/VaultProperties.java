package ru.yandex.autotests.metrika.appmetrica.properties;

import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

@Resource.Classpath("vault.properties")
public class VaultProperties {
    private static VaultProperties instance;

    private VaultProperties() {
        PropertyLoader.populate(this);
    }

    public static VaultProperties getInstance() {
        if (instance == null) {
            instance = new VaultProperties();
        }
        return instance;
    }

    /**
     * Идентификатор секрета, откуда подгружаются данные пользователей
     */
    @Property("users.secretid")
    private String usersSecretId;

    public String getUsersSecretId() {
        return usersSecretId;
    }
}

