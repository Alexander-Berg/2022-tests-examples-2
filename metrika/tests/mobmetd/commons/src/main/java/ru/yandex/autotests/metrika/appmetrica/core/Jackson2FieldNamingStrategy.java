package ru.yandex.autotests.metrika.appmetrica.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.gson.FieldNamingPolicy;
import com.google.gson.FieldNamingStrategy;

import java.lang.reflect.Field;

/**
 * Стратегия преобразования имен полей из Java в json на основе аннотаций Jackson2.
 * В случае отсутствия аннотации осуществляет преобразование FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES
 * <p>
 * Данная стратегия необходима для корректной сериализации и десериализации полей, которые в json имеют вид "class",
 * т.е. зарезервированные ключевые слова.
 */
public class Jackson2FieldNamingStrategy implements FieldNamingStrategy {

    public static FieldNamingStrategy STRATEGY = new Jackson2FieldNamingStrategy();

    @Override
    public String translateName(Field field) {

        JsonProperty jsonProperty = field.getAnnotation(JsonProperty.class);

        return jsonProperty != null
                ? jsonProperty.value()
                : FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES.translateName(field);
    }
}
