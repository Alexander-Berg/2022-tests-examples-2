package ru.yandex.autotests.metrika.appmetrica.data;

import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;

import ru.yandex.autotests.metrika.appmetrica.properties.VaultProperties;
import ru.yandex.autotests.metrika.commons.propertybag.PropertyBag;
import ru.yandex.autotests.metrika.commons.vault.VaultClient;

public class User extends PropertyBag<User> {

    public static final PropertyDescriptor<String, User> LOGIN = prop("login", String.class, User.class);
    public static final PropertyDescriptor<String, User> PASSWORD = prop("password", String.class, User.class);
    public static final PropertyDescriptor<String, User> OAUTH_TOKEN = prop("oauth_token", String.class, User.class);
    public static final PropertyDescriptor<String, User> UID = prop("uid", String.class, User.class);

    private static final Map<String, String> SECRET_CONTENT = VaultClient.loadLastVersion(VaultProperties.getInstance().getUsersSecretId());
    private static final Gson GSON = new GsonBuilder().create();

    public User(String login) {
        put(LOGIN, login);
    }

    public User putSecret(String secretKey) {
        Map<String, String> content = GSON.fromJson(SECRET_CONTENT.get(secretKey), new TypeToken<Map<String, String>>(){}.getType());
        if (content.containsKey(PASSWORD.getName())) {
            this.put(PASSWORD, content.get(PASSWORD.getName()));
        }
        if (content.containsKey(OAUTH_TOKEN.getName())) {
            this.put(OAUTH_TOKEN, content.get(OAUTH_TOKEN.getName()));
        }
        return this;
    }

    @Override
    protected User getThis() {
        return this;
    }

    public long getUid() {
        return Long.parseLong(get(UID));
    }

    @Override
    public String toString() {
        return get(LOGIN);
    }
}
