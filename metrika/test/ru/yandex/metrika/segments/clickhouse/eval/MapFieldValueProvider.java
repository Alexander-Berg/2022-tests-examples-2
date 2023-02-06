package ru.yandex.metrika.segments.clickhouse.eval;

import java.util.HashMap;
import java.util.Map;

import javax.annotation.Nonnull;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.ast.Field;
import ru.yandex.metrika.segments.clickhouse.types.CHType;

public class MapFieldValueProvider implements FieldValueProvider {
    private final Map<Field<?>, CHLiteral<?>> fieldValues;

    public MapFieldValueProvider() {
        fieldValues = new HashMap<>();
    }

    MapFieldValueProvider(Map<Field<?>, CHLiteral<?>> fieldValues) {
        this.fieldValues = fieldValues;
    }

    @Nonnull
    @Override
    public <T extends CHType> CHLiteral<T> getFieldValue(Field<T> field) {
        //noinspection unchecked
        return (CHLiteral<T>) fieldValues.get(field);
    }

    public <T extends CHType> void putFieldValue(Field<T> field, CHLiteral<T> value) {
        fieldValues.put(field, value);
    }
}
