package ru.yandex.autotests.advapi.converters;

import java.util.Map;
import java.util.Objects;
import java.util.function.Function;

/**
 * Created by konkov on 18.12.2014.
 * <p>
 * Функция для извлечения значения измерения в виде человеко-читаемой строки,
 * null преобразуется в заданную строку
 * особо обрабатываются поля direct_id и url
 */
public class DimensionToHumanReadableStringMapper implements Function<Map<String, String>, String> {

    public final static String NULL_RU = "Не определено";

    private final static String[] EXCEL_KEYS = new String[]{"direct_id"};

    private String nullRepresentation;

    public DimensionToHumanReadableStringMapper() {
        nullRepresentation = NULL_RU;
    }

    public DimensionToHumanReadableStringMapper(String nullRepresentation) {
        this.nullRepresentation = nullRepresentation;
    }

    public static DimensionToHumanReadableStringMapper dimensionToHumanReadableStringMapper() {
        return new DimensionToHumanReadableStringMapper();
    }

    public static DimensionToHumanReadableStringMapper dimensionToHumanReadableStringMapper(
            String nullRepresentation) {
        return new DimensionToHumanReadableStringMapper(nullRepresentation);
    }

    @Override
    public String apply(Map<String, String> from) {
        StringBuilder stringBuilder = new StringBuilder();

        Object name = from.get("name");

        stringBuilder.append(Objects.toString(name, nullRepresentation));

        if (name != null) {
            for (String key : EXCEL_KEYS) {
                handleKey(from, key, stringBuilder);
            }
        }

        return stringBuilder.toString();
    }

    private void handleKey(Map<String, String> dimensionRawValue, String key, StringBuilder stringBuilder) {
        if (dimensionRawValue.containsKey(key)) {
            stringBuilder.append(" ( ")
                    .append(dimensionRawValue.get(key))
                    .append(" )");
        }
    }
}
