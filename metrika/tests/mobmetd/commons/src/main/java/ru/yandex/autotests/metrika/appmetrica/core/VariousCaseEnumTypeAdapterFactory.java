package ru.yandex.autotests.metrika.appmetrica.core;

import com.google.gson.Gson;
import com.google.gson.TypeAdapter;
import com.google.gson.TypeAdapterFactory;
import com.google.gson.reflect.TypeToken;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import com.google.gson.stream.JsonWriter;
import org.apache.commons.lang3.RandomUtils;

import java.io.IOException;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Пишет enum в json в случайном регистре.
 * При чтении ищет совпадение enum-значения и значения из json в нижнем регистре.
 */
public class VariousCaseEnumTypeAdapterFactory implements TypeAdapterFactory {
    public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type) {
        Class<T> rawType = (Class<T>) type.getRawType();
        if (!rawType.isEnum()) {
            return null;
        }

        final Map<String, T> lowercaseToConstant = new HashMap<>();
        for (T constant : rawType.getEnumConstants()) {
            lowercaseToConstant.put(toLowercase(constant), constant);
        }

        return new TypeAdapter<T>() {
            public void write(JsonWriter out, T value) throws IOException {
                if (value == null) {
                    out.nullValue();
                } else {
                    out.value(toRandomCase(value.toString()));
                }
            }

            public T read(JsonReader reader) throws IOException {
                if (reader.peek() == JsonToken.NULL) {
                    reader.nextNull();
                    return null;
                } else {
                    return lowercaseToConstant.get(toLowercase(reader.nextString()));
                }
            }
        };
    }

    private String toRandomCase(Object o) {
        if (RandomUtils.nextBoolean()) {
            return o.toString().toLowerCase(Locale.US);
        } else {
            return o.toString().toUpperCase(Locale.US);
        }
    }

    private String toLowercase(Object o) {
        return o.toString().toLowerCase(Locale.US);
    }
}