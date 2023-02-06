package ru.yandex.autotests.metrika.core.jodatime;

import com.google.gson.*;
import com.google.gson.reflect.TypeToken;
import org.joda.time.LocalTime;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.ISODateTimeFormat;

import java.lang.reflect.Type;

/**
 * @author zgmnkv
 */
public class LocalTimeConverter implements JsonSerializer<LocalTime>, JsonDeserializer<LocalTime> {

    public static final Type LOCAL_TIME_TYPE = new TypeToken<LocalTime>(){}.getType();

    private DateTimeFormatter formatter = ISODateTimeFormat.time();
    private DateTimeFormatter parser = ISODateTimeFormat.localTimeParser();

    @Override
    public JsonElement serialize(LocalTime src, Type typeOfSrc, JsonSerializationContext context) {
        return new JsonPrimitive(formatter.print(src));
    }

    @Override
    public LocalTime deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context) {
        String stringValue = json.getAsString();
        if (stringValue == null || stringValue.isEmpty()) {
            return null;
        }
        return parser.parseLocalTime(stringValue);
    }
}
