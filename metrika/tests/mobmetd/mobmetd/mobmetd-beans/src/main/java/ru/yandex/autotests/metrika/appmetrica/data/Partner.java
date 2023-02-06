package ru.yandex.autotests.metrika.appmetrica.data;

import ru.yandex.autotests.metrika.commons.propertybag.PropertyBag;

/**
 * Created by graev on 01/12/2016.
 */
public class Partner extends PropertyBag<Partner> {
    public static final PropertyDescriptor<Long, Partner> ID = prop("id", Long.class, Partner.class);
    public static final PropertyDescriptor<String, Partner> NAME = prop("name", String.class, Partner.class);

    public Partner(Long id) {
        put(ID, id);
    }

    @Override
    protected Partner getThis() {
        return this;
    }

    @Override
    public String toString() {
        return get(NAME);
    }
}
