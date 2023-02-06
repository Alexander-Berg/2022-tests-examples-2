package ru.yandex.autotests.morda.api.cleanvars.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import ru.yandex.autotests.morda.beans.cleanvars.geo.Maps;

import java.io.IOException;

public class MordaCleanvarsMapsDeserializer extends JsonDeserializer<Maps> {

    @Override
    public Maps deserialize(JsonParser jp, DeserializationContext ctxt)
            throws IOException {

        if (jp.isExpectedStartObjectToken()) {
            return jp.readValueAs(Maps.class);
        } else {
            return new Maps().withMaps(jp.readValueAs(Integer.class));
        }
    }
}