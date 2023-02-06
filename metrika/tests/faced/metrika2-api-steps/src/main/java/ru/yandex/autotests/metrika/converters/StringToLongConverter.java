package ru.yandex.autotests.metrika.converters;

import ch.lambdaj.function.convert.Converter;

/**
 * Created by konkov on 16.06.2015.
 */
public class StringToLongConverter implements Converter<String, Long> {
    @Override
    public Long convert(String from) {
        return Long.valueOf(from);
    }
}
