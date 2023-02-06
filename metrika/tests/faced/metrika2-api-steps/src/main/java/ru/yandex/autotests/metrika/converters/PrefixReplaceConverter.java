package ru.yandex.autotests.metrika.converters;

import ch.lambdaj.function.convert.StringConverter;

/**
 * Created by konkov on 15.06.2015.
 */
public class PrefixReplaceConverter implements StringConverter<String> {

    private final String fromPrefix;
    private final String toPrefix;

    public PrefixReplaceConverter(String fromPrefix, String toPrefix) {
        this.fromPrefix = fromPrefix;
        this.toPrefix = toPrefix;
    }

    @Override
    public String convert(String from) {
        return from.startsWith(fromPrefix)
                ? toPrefix + from.substring(fromPrefix.length())
                : from;
    }
}
