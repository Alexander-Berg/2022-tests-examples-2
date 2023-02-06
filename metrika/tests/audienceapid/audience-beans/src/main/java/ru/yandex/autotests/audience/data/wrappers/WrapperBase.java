package ru.yandex.autotests.audience.data.wrappers;

import com.rits.cloning.Cloner;
import org.apache.commons.lang3.builder.ReflectionToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;

/**
 * Created by konkov on 28.03.2017.
 */
public class WrapperBase<T> {
    private final static Cloner CLONER = new Cloner();

    protected final T value;

    protected WrapperBase(T value) {
        this.value = value;
    }

    public static <U> WrapperBase<U> wrap(U value) {
        return new WrapperBase<>(value);
    }

    public T get() {
        return value;
    }

    public T getClone() {
        return CLONER.deepClone(value);
    }

    @Override
    public String toString() {
        return value == null ? "<null>"
                : ReflectionToStringBuilder.toString(value, ToStringStyle.SHORT_PREFIX_STYLE);
    }
}
