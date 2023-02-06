package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import org.joda.time.LocalDateTime;
import org.joda.time.LocalTime;

import java.io.IOException;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/15
 */
public class TillDateTimeDeserializer extends DateTimeDeserializer {

    @Override
    public LocalDateTime deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        LocalDateTime time = parseDateTime(p.getText());

        if (time.toLocalTime().equals(LocalTime.MIDNIGHT)) {
            time = time.plusDays(1);
        }

        return time;
    }
}
