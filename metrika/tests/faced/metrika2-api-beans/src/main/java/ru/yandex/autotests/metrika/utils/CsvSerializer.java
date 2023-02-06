package ru.yandex.autotests.metrika.utils;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Lists;
import org.apache.commons.lang3.StringUtils;

import java.lang.reflect.Field;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * CSV сериализатор общего назначения.
 * Можно серилизовать сырые строки, или pojo объекты.
 * При сериализации объектов поля для сериализации должны быть проаннотированы аннотацией {@link CsvField}.
 * При сериализации объектов добавляется первая строка с заголовками колонок.
 *
 * @author zgmnkv
 */
public class CsvSerializer {

    private String quote = "\"";
    private String separator = ",";
    private String lineSeparator = "\n";

    public <T> String serialize(Class<T> type, List<T> items) {
        List<CsvFieldDescriptor> fields = getFields(type);

        return serialize(ImmutableList.<List<String>>builder()
                .add(getHeaderRow(fields))
                .addAll(Lists.transform(items, item -> getRow(fields, item)))
                .build()
        );
    }

    public String serialize(List<List<String>> rows) {
        return rows.stream()
                .map(this::serializeRow)
                .collect(Collectors.joining(lineSeparator));
    }



    public String getQuote() {
        return quote;
    }

    public void setQuote(String quote) {
        this.quote = quote;
    }

    public CsvSerializer withQuote(String quote) {
        this.quote = quote;
        return this;
    }

    public String getSeparator() {
        return separator;
    }

    public void setSeparator(String separator) {
        this.separator = separator;
    }

    public CsvSerializer withSeparator(String separator) {
        this.separator = separator;
        return this;
    }

    public String getLineSeparator() {
        return lineSeparator;
    }

    public void setLineSeparator(String lineSeparator) {
        this.lineSeparator = lineSeparator;
    }

    public CsvSerializer withLineSeparator(String lineSeparator) {
        this.lineSeparator = lineSeparator;
        return this;
    }



    private List<CsvFieldDescriptor> getFields(Class<?> type) {
        List<Class<?>> hierarchy = new ArrayList<>();

        Class<?> tmpType = type;
        do {
            hierarchy.add(tmpType);
            tmpType = tmpType.getSuperclass();
        } while (tmpType != null);

        Collections.reverse(hierarchy);

        return hierarchy.stream()
                .flatMap(t -> Stream.of(t.getDeclaredFields())
                        .flatMap(field -> {
                            CsvField csvField = field.getAnnotation(CsvField.class);
                            return csvField != null ? Stream.of(new CsvFieldDescriptor(field, csvField)) : Stream.empty();
                        })
                )
                .sorted(Comparator.comparing(fieldDescriptor -> fieldDescriptor.getCsvField().order()))
                .collect(Collectors.toList());
    }

    private List<String> getHeaderRow(List<CsvFieldDescriptor> fields) {
        return fields.stream()
                .map(field -> field.getCsvField().value())
                .collect(Collectors.toList());
    }

    private List<String> getRow(List<CsvFieldDescriptor> fields, Object item) {
        return fields.stream()
                .map(field -> {
                    try {
                        field.getField().setAccessible(true);
                        return field.getField().get(item);
                    } catch (IllegalAccessException e) {
                        throw new RuntimeException(e);
                    }
                })
                .map(value -> Objects.toString(value, StringUtils.EMPTY))
                .collect(Collectors.toList());
    }

    private String serializeRow(List<String> row) {
        return row.stream()
                .map(this::quoteIfNeeded)
                .collect(Collectors.joining(separator));
    }

    private String quoteIfNeeded(String value) {
        if (StringUtils.containsAny(value, quote, separator, lineSeparator, "\n", "\r")) {
            return quote + value.replace(quote, quote + quote) + quote;
        } else {
            return value;
        }
    }

    private static class CsvFieldDescriptor {

        private Field field;
        private CsvField csvField;

        public CsvFieldDescriptor(Field field, CsvField csvField) {
            this.field = field;
            this.csvField = csvField;
        }

        public Field getField() {
            return field;
        }

        public CsvField getCsvField() {
            return csvField;
        }
    }
}
