package ru.yandex.autotests.advapi.converters;

import java.util.Map;
import java.util.function.Function;

/**
 * Created by konkov on 18.12.2014.
 * <p>
 * Функция для извлечения значения измерения в виде человеко-читаемой строки,
 * null преобразуется в заданную строку
 */
public class DimensionToNameMapper implements Function<Map<String, String>, String> {

    public final static String NULL_RU = "Не определено";

    private String nullRepresentation;

    public DimensionToNameMapper() {
        nullRepresentation = NULL_RU;
    }

    public DimensionToNameMapper(String nullRepresentation) {
        this.nullRepresentation = nullRepresentation;
    }

    @Override
    public String apply(Map<String, String> from) {
        return from.getOrDefault("name", nullRepresentation);
    }
}
