package ru.yandex.autotests.internalapid.beans.data;

import com.google.common.reflect.TypeToken;
import ru.yandex.autotests.metrika.commons.propertybag.PropertyBag;
import ru.yandex.metrika.api.management.client.external.CounterSource;

import java.util.List;

public class Counter extends PropertyBag<Counter> {
    public static final PropertyDescriptor<String, Counter> NAME = prop("name", String.class, Counter.class);
    public static final PropertyDescriptor<Long, Counter> ID = prop("id", Long.class, Counter.class);
    public static final PropertyDescriptor<Long, Counter> GOAL_ID = prop("goal_id", Long.class, Counter.class);
    public static final PropertyDescriptor<Long, Counter> EXPERIMENT_ID = prop("experiment_id", Long.class, Counter.class);
    public static final PropertyDescriptor<String, Counter> U_LOGIN = prop("u_login", String.class, Counter.class);
    public static final PropertyDescriptor<List<Long>, Counter> CLIENT_IDS = prop("client_ids",
            (Class<List<Long>>) new TypeToken<List<Long>>(){}.getRawType(), Counter.class);

    public Counter(String login) {
        put(NAME, login);
    }

    public long getId() {
        return get(ID);
    }

    @Override
    protected Counter getThis() {
        return this;
    }

    @Override
    public String toString() {
        return get(NAME);
    }
}
