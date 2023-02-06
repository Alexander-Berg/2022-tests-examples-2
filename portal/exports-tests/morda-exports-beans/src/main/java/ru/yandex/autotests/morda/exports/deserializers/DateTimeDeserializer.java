package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import org.joda.time.LocalDateTime;
import org.joda.time.format.DateTimeFormatter;

import java.io.IOException;
import java.util.List;

import static java.util.Arrays.asList;
import static org.joda.time.format.DateTimeFormat.forPattern;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/15
 */
public class DateTimeDeserializer extends JsonDeserializer<LocalDateTime> {

    protected LocalDateTime parseDateTime(String date) {

        List<DateTimeFormatter> formats = asList(
                forPattern("yyyy-MM-dd HH:mm:ss"),
                forPattern("yyyy-MM-dd HH:mm"),
                forPattern("yyyy-MM-dd")
        );

        for (DateTimeFormatter f : formats) {
            LocalDateTime time = tryParse(f, date);
            if (time != null) {
                return time;
            }
        }

        throw new IllegalArgumentException("Failed to parse LocalDateTime from \"" + date + "\"");
    }

    private LocalDateTime tryParse(DateTimeFormatter formatter, String date) {
        try {
            return formatter.parseLocalDateTime(date.trim());
        } catch (IllegalArgumentException e) {
            return null;
        }
    }

    @Override
    public LocalDateTime deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        return parseDateTime(p.getText());
    }
}
