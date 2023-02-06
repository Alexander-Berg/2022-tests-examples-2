package ru.yandex.autotests.metrika.beans.schemes;

import ru.yandex.metrika.api.management.client.operation.OperationE;

/**
 * @see ru.yandex.metrika.util.wrappers.OperationWrapper
 * Created by konkov on 19.10.2015.
 */
public class OperationEObjectWrapper {
    private final OperationE value;

    public OperationEObjectWrapper(OperationE value) {
        this.value = value;
    }

    public OperationE get() {
        return value;
    }

    @Override
    public String toString() {
        return value == null ? "null"
                : new StringBuilder()
                .append("action: ").append(value.getAction())
                .append(" attr: ").append(value.getAttr())
                .append(" value: ").append(value.getValue())
                .append(" status: ").append(value.getStatus())
                .toString();
    }

}
