package ru.yandex.autotests.metrika.beans.schemes;

import ru.yandex.metrika.api.management.client.external.CounterGrantRequest;

/**
 * @see ru.yandex.metrika.util.wrappers.CounterGrantRequestWrapper
 * Created by konkov on 09.12.2015.
 */
public class CounterGrantRequestObjectWrapper {
    private final CounterGrantRequest value;

    public CounterGrantRequestObjectWrapper(CounterGrantRequest value) {
        this.value = value;
    }

    public CounterGrantRequest get() {
        return value;
    }

    @Override
    public String toString() {
        return value == null ? "null" : "login: " + value.getUserLogin();
    }
}
