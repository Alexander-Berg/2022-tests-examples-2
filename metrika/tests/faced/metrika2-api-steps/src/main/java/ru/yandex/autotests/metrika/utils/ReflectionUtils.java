package ru.yandex.autotests.metrika.utils;

import org.apache.commons.beanutils.PropertyUtils;

import static com.google.common.base.Throwables.propagate;

/**
 * Created by konkov on 12.07.2016.
 */
public final class ReflectionUtils {
    private ReflectionUtils() {}

    public static <T> T getProperty(Object object, String name) {
        try {
            return (T) PropertyUtils.getProperty(object, name);
        } catch (Throwable e) {
            throw propagate(e);
        }
    }
}
