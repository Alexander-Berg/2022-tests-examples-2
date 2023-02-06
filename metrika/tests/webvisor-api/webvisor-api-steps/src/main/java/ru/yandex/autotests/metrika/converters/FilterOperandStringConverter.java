package ru.yandex.autotests.metrika.converters;

import ch.lambdaj.function.convert.StringConverter;

import static ru.yandex.autotests.metrika.utils.Utils.wrapFilterValue;

/**
 * Created by konkov on 30.06.2015.
 */
public class FilterOperandStringConverter implements StringConverter {
    @Override
    public String convert(Object from) {
        return wrapFilterValue(from);
    }
}
