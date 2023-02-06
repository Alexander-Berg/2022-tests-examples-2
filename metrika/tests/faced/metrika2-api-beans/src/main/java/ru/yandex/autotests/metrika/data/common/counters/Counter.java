package ru.yandex.autotests.metrika.data.common.counters;

import com.google.common.reflect.TypeToken;
import ru.yandex.autotests.metrika.commons.propertybag.PropertyBag;

import java.util.List;

/**
 * Created by vananos on 15.08.16.
 */
public class Counter extends PropertyBag<Counter> {
    public static final PropertyDescriptor<String, Counter> NAME = prop("name", String.class, Counter.class);
    public static final PropertyDescriptor<Long, Counter> ID = prop("id", Long.class, Counter.class);
    public static final PropertyDescriptor<Long, Counter> GOAL_ID = prop("goal_id", Long.class, Counter.class);
    public static final PropertyDescriptor<Long, Counter> EXPERIMENT_ID = prop("experiment_id", Long.class, Counter.class);
    public static final PropertyDescriptor<String, Counter> U_LOGIN = prop("u_login", String.class, Counter.class);
    public static final PropertyDescriptor<List<Long>, Counter> CLIENT_IDS = prop("client_ids",
            (Class<List<Long>>) new TypeToken<List<Long>>(){}.getRawType(), Counter.class);
    public static final PropertyDescriptor<List<String>, Counter> REFERENCE_ROW_ID = prop("reference_row_id",
            (Class<List<String>>) new TypeToken<List<String>>(){}.getRawType(), Counter.class);

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