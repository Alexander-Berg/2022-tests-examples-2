package ru.yandex.autotests.metrika.core.jodatime;

import com.google.gson.*;
import com.google.gson.reflect.TypeToken;
import org.joda.time.LocalDate;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

import java.lang.reflect.Type;

/**
 * @author zgmnkv
 */
public class LocalDateConverter implements JsonSerializer<LocalDate>, JsonDeserializer<LocalDate> {

    public static final Type LOCAL_DATE_TYPE = new TypeToken<LocalDate>(){}.getType();

    private static final String PATTERN = "yyyy-MM-dd";

    private DateTimeFormatter formatter = DateTimeFormat.forPattern(PATTERN);
    private DateTimeFormatter parser = formatter;

    @Override
    public JsonElement serialize(LocalDate src, Type typeOfSrc, JsonSerializationContext context) {
        return new JsonPrimitive(formatter.print(src));
    }

    @Override
    public LocalDate deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context) {
        String stringValue = json.getAsString();
        if (stringValue == null || stringValue.isEmpty()) {
            return null;
        }
        return parser.parseLocalDate(stringValue);
    }
}
