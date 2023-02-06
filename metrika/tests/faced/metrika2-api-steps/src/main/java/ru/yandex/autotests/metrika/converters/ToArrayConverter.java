package ru.yandex.autotests.metrika.converters;

import ch.lambdaj.function.convert.Converter;

import static org.apache.commons.lang3.ArrayUtils.toArray;

/**
 * Created by konkov on 03.09.2014.
 *
 * Конвертер предназначен для преобразования объекта в массив из одного элемента.
 * Использование - формирование параметров теста.
 */
public class ToArrayConverter<From> implements Converter<From, Object[]> {
    @Override
    public Object[] convert(From from) {
        return toArray(from);
    }
}
