package ru.yandex.autotests.metrika.core.jodatime;

import com.google.gson.*;
import com.google.gson.reflect.TypeToken;
import org.joda.time.LocalDateTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

import java.lang.reflect.Type;

/**
 * @author zgmnkv
 */
public class LocalDateTimeConverter implements JsonSerializer<LocalDateTime>, JsonDeserializer<LocalDateTime> {

    public static final Type LOCAL_DATE_TIME_TYPE = new TypeToken<LocalDateTime>(){}.getType();

    private static final String PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSS";

    private DateTimeFormatter formatter = DateTimeFormat.forPattern(PATTERN);
    private DateTimeFormatter parser = formatter;

    @Override
    public JsonElement serialize(LocalDateTime src, Type typeOfSrc, JsonSerializationContext context) {
        return new JsonPrimitive(formatter.print(src));
    }

    @Override
    public LocalDateTime deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context) {
        String stringValue = json.getAsString();
        if (stringValue == null || stringValue.isEmpty()) {
            return null;
        }
        return parser.parseLocalDateTime(stringValue);
    }
}
