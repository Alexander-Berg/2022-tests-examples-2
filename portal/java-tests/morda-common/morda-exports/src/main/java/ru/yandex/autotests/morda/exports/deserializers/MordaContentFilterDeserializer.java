package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import ru.yandex.autotests.morda.exports.filters.MordaContentFilter;

import java.io.IOException;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/15
 */
public class MordaContentFilterDeserializer extends JsonDeserializer<MordaContentFilter> {
    @Override
    public MordaContentFilter deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        final String value = p.getText();
        return MordaContentFilter.fromString(value);
    }
}
