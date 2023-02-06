package ru.yandex.autotests.metrika.beans.schemes;

import com.rits.cloning.Cloner;
import ru.yandex.metrika.api.management.client.external.CounterFull;

/**
 * Created by konkov on 03.03.2015.
 */
public class CounterFullObjectWrapper {
    private final CounterFull value;

    public CounterFullObjectWrapper(CounterFull value) {
        this.value = value;
    }

    public CounterFull get() {
        return value;
    }

    private final static Cloner CLONER = new Cloner();

    @Override
    public String toString() {
        return value == null ? "null"
                : value.getName();
    }

    public CounterFull getClone() {
        return CLONER.deepClone(value);
    }
}
