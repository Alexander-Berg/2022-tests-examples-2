package ru.yandex.autotests.audience.data.users;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import ru.yandex.autotests.audience.properties.VaultProperties;
import ru.yandex.autotests.metrika.commons.propertybag.PropertyBag;
import ru.yandex.autotests.metrika.commons.vault.VaultClient;

import java.util.List;
import java.util.Map;

public class User extends PropertyBag<User> {
    public static final PropertyDescriptor<String, User> PASSWORD = prop("password", String.class, User.class);
    public static final PropertyDescriptor<String, User> OAUTH_TOKEN = prop("oauth_token", String.class, User.class);
    public static final PropertyDescriptor<String, User> LOGIN = prop("login", String.class, User.class);
    public static final PropertyDescriptor<Long, User> METRIKA_COUNTER_ID = prop("metrika_counter_id", Long.class, User.class);
    public static final PropertyDescriptor<Long, User> METRIKA_GOAL_ID = prop("metrika_goal_id", Long.class, User.class);
    public static final PropertyDescriptor<Long, User> METRIKA_SEGMENT_ID = prop("metrika_segment_id", Long.class, User.class);
    public static final PropertyDescriptor<Long, User> APPMETRICA_APLICATION_ID = prop("appmetrica_application_id", Long.class, User.class);
    public static final PropertyDescriptor<String, User> APPMETRICA_API_KEY = prop("appmetrica_api_key", String.class, User.class);
    public static final PropertyDescriptor<Long, User> APPMETRICA_SEGMENT_ID = prop("appmetrica_segment_id", Long.class, User.class);
    public static final PropertyDescriptor<List, User> METRIKA_GOALS_IDS = prop("metrika goals", List.class, User.class);
    public static final PropertyDescriptor<Long, User> ANOTHER_METRIKA_COUNTER = prop("another metrika_counter_id", Long.class, User.class);
    public static final PropertyDescriptor<List, User> ANOTHER_COUNTER_GOAL_IDS = prop("another counter goal_ids", List.class, User.class);
    public static final PropertyDescriptor<Long, User> GEO_SEGMENT_ID = prop("audience_geo_segment_id", Long.class, User.class);
    public static final PropertyDescriptor<Long, User> AUDIENCE_METRIKA_SEGMENT_ID = prop("audience_metrika_segment_id", Long.class, User.class);
    public static final PropertyDescriptor<Long, User> AUDIENCE_APPMETRICA_SEGMENT_ID = prop("audience_appmetrica_segment_id", Long.class, User.class);

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

    @Override
    public String toString() {
        return get(LOGIN);
    }
}

