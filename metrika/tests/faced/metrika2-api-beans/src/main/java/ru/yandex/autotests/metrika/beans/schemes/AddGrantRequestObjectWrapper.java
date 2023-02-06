package ru.yandex.autotests.metrika.beans.schemes;

import org.apache.commons.beanutils.BeanUtils;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiWrapperException;
import ru.yandex.metrika.api.management.client.AddGrantRequest;

import java.lang.reflect.InvocationTargetException;

/**
 * Created by konkov on 08.12.2015.
 */
public class AddGrantRequestObjectWrapper {
    private final AddGrantRequest value;

    public AddGrantRequestObjectWrapper(AddGrantRequest value) {
        this.value = value;
    }

    public AddGrantRequest get() {
        return value;
    }

    @Override
    public String toString() {
        return value == null ? "null"
                : new StringBuilder()
                .append("requestor: ").append(value.getRequestorLogin())
                .append(" perm: ").append(value.getPermission())
                .append(" owner: ").append(value.getOwnerLogin())
                .toString();
    }

    public AddGrantRequest getClone() {
        try {
            return (AddGrantRequest) BeanUtils.cloneBean(value);
        } catch (IllegalAccessException |
                InstantiationException |
                InvocationTargetException |
                NoSuchMethodException e) {
            throw new MetrikaApiWrapperException("Ошибка при клонировании объекта", e);
        }
    }
}
