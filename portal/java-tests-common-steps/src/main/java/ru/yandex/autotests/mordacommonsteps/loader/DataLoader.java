package ru.yandex.autotests.mordacommonsteps.loader;

import ru.yandex.autotests.utils.morda.url.Domain;

import java.lang.reflect.Field;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.05.13
 */

public class DataLoader {

    public static void populate(Class clazz, Domain domain) {
        populate(clazz, new DefaultDomainDecorator(), domain);
    }

    public static void populate(Class clazz, DomainDecorator decorator, Domain domain) {
        Class c = clazz;
        while (c != Object.class) {
            initFields(decorator, c, domain);
            c = c.getSuperclass();
        }
    }

    private static void initFields(DomainDecorator decorator, Class<?> clazz, Domain domain) {
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            Object value = decorator.decorate(field, domain);
            setValue(field, clazz, value);
        }
    }

    private static void setValue(Field field, Class clazz, Object value) {
        if (value != null) {
            try {
                field.setAccessible(true);
                field.set(clazz, value);
            } catch (IllegalAccessException e) {
                throw new RuntimeException(e);
            }
        }
    }
}
