package ru.yandex.autotests.mordacommonsteps.utils;

import org.apache.commons.beanutils.Converter;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * User: eoff
 * Date: 15.03.13
 */
public class ListConverter implements Converter {
    private String delimiter;

    public ListConverter(String delimiter) {
        this.delimiter = delimiter;
    }

    @Override
    public Object convert(Class aClass, Object o) {
        if (!(o instanceof String)) {
            return new ArrayList<String>();
        }
        String str = (String) o;
        return Arrays.asList(str.split(delimiter));
    }
}
