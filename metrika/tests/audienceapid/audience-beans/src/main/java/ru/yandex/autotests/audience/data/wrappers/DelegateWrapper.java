package ru.yandex.autotests.audience.data.wrappers;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import ru.yandex.metrika.audience.pubapi.Delegate;

/**
 * Created by ava1on on 05.07.17.
 */
public class DelegateWrapper extends WrapperBase<Delegate> {
    protected DelegateWrapper(Delegate value) {
        super(value);
    }

    public static DelegateWrapper wrap(Delegate value) {
        return new DelegateWrapper(value);
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this.get(), ToStringStyle.JSON_STYLE);
    }
}
