package ru.yandex.autotests.metrika.appmetrica.data;

import ru.yandex.autotests.metrika.commons.propertybag.PropertyBag;

public class Application extends PropertyBag<Application> {
    public static final PropertyDescriptor<Long, Application> ID = prop("id", Long.class, Application.class);
    public static final PropertyDescriptor<String, Application> NAME = prop("name", String.class, Application.class);
    public static final PropertyDescriptor<Integer, Application> LAYER = prop("layer", Integer.class, Application.class);

    public Application(String name) {
        put(NAME, name);
    }

    @Override
    protected Application getThis() {
        return this;
    }

    @Override
    public String toString() {
        return get(NAME);
    }
}
