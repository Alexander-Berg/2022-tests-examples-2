package ru.yandex.autotests.audience.core;

import com.google.gson.*;
import org.apache.commons.lang3.tuple.Pair;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.SegmentType;
import ru.yandex.audience.geo.GeoSegmentForm;

import java.lang.reflect.Type;
import java.util.LinkedHashMap;
import java.util.Map;

import javax.annotation.Nullable;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * Created by konkov on 24.03.2017.
 */
public class SegmentDeserializer implements JsonDeserializer<BaseSegment> {

    public static final String TYPE_FIELD_NAME = "type";
    public static final String SHAPE_FIELD_NAME = "form";

    private final Map<Pair<SegmentType, GeoSegmentForm>, Class<?>> labelToSubtype = new LinkedHashMap<>();

    public SegmentDeserializer registerSegmentType(Class<? extends BaseSegment> type, SegmentType label, @Nullable GeoSegmentForm shape) {
        checkNotNull(type);
        checkNotNull(label);

        if (type.equals(BaseSegment.class)) {
            throw new IllegalArgumentException("Базовый тип BaseSegment не поддерживается");
        }

        if (label == SegmentType.GEO && shape == null) {
            throw new IllegalArgumentException("для геосегментов нужно указать форму");
        }

        Pair<SegmentType, GeoSegmentForm> key = Pair.of(label, shape);
        if (labelToSubtype.containsKey(key)) {
            throw new IllegalArgumentException("типы должны быть уникальными");
        }

        labelToSubtype.put(key, type);

        return this;
    }

    public SegmentDeserializer registerSegmentType(Class<? extends BaseSegment> type, SegmentType label) {
        return registerSegmentType(type, label, null);
    }

    @Override
    public BaseSegment deserialize(JsonElement jsonElement,
                                   Type type,
                                   JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
        BaseSegment entity;

        try {
            JsonObject jsonObject = (JsonObject) jsonElement;

            SegmentType actualType = jsonDeserializationContext
                    .deserialize(jsonObject.get(TYPE_FIELD_NAME), SegmentType.class);

            GeoSegmentForm shape = jsonDeserializationContext
                    .deserialize(jsonObject.get(SHAPE_FIELD_NAME), GeoSegmentForm.class);

            Class<?> aClass = labelToSubtype.get(Pair.of(actualType, shape));

            entity = jsonDeserializationContext.deserialize(jsonElement, aClass);

        } catch (Throwable e) {
            throw new JsonParseException(String.format("Ошибка десериализации %s из %s", type, jsonElement), e);
        }

        return entity;
    }
}
