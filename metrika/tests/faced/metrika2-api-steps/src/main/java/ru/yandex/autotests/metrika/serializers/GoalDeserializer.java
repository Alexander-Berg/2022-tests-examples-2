package ru.yandex.autotests.metrika.serializers;

import com.google.gson.*;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;

import java.lang.reflect.Type;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Created by konkov on 20.03.2015.
 */
public class GoalDeserializer implements JsonDeserializer<GoalE> {

    public static final String TYPE_FIELD_NAME = "type";
    private final Map<GoalType, Class<?>> labelToSubtype = new LinkedHashMap<>();

    public GoalDeserializer registerGoalType(Class<? extends GoalE> type, GoalType label) {
        if (type == null || label == null) {
            throw new NullPointerException();
        }
        if (type.equals(GoalE.class)) {
            throw new IllegalArgumentException("Базовый тип GoalE не поддерживается");
        }
        if (labelToSubtype.containsKey(label)) {
            throw new IllegalArgumentException("типы должны быть уникальными");
        }
        labelToSubtype.put(label, type);
        return this;
    }

    @Override
    public GoalE deserialize(JsonElement jsonElement,
                                   Type type,
                                   JsonDeserializationContext jsonDeserializationContext)
            throws JsonParseException {

        GoalE entity;

        try {
            JsonObject jsonObject = (JsonObject) jsonElement;

            GoalType actualType = jsonDeserializationContext
                    .deserialize(jsonObject.get(TYPE_FIELD_NAME), GoalType.class);

            //здесь на основе актуального типа получаем класс десериализуемого элемента
            Class<?> aClass = labelToSubtype.get(actualType);
            //и делегируем десериализацию текущего элемента в актуальный тип
            entity = jsonDeserializationContext.deserialize(jsonElement, aClass);
        } catch (Exception e) {
            throw new JsonParseException(String.format("Ошибка десериализации %s из %s", type.toString(),
                    jsonElement.toString()), e);
        }

        return entity;
    }
}
