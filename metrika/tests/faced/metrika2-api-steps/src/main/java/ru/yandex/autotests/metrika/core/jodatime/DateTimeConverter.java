package ru.yandex.autotests.metrika.core.jodatime;

import com.google.gson.*;
import com.google.gson.reflect.TypeToken;
import org.joda.time.DateTime;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.format.ISODateTimeFormat;

import java.lang.reflect.Type;

/**
 * @author zgmnkv
 */
public class DateTimeConverter implements JsonSerializer<DateTime>, JsonDeserializer<DateTime> {

    public static final Type DATE_TIME_TYPE = new TypeToken<DateTime>(){}.getType();

    private DateTimeFormatter formatter = ISODateTimeFormat.dateTime();
    private DateTimeFormatter parser = ISODateTimeFormat.dateTimeParser().withOffsetParsed();

    @Override
    public JsonElement serialize(DateTime src, Type typeOfSrc, JsonSerializationContext context) {
        return new JsonPrimitive(formatter.print(src));
    }

    @Override
    public DateTime deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context) {
        String stringValue = json.getAsString();
        if (stringValue == null || stringValue.isEmpty()) {
            return null;
        }
        return parser.parseDateTime(stringValue);
    }
}
