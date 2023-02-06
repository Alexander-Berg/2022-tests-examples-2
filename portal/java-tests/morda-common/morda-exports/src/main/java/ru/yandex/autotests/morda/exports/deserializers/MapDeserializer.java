package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public abstract class MapDeserializer<T> extends ExportDataDeserializer<T> {

    @Override
    protected Iterator<JsonNode> getItems(JsonParser jsonParser) throws IOException {
        final JsonNode root = jsonParser.readValueAs(JsonNode.class);
        final List<JsonNode> result = new ArrayList<>();

        root.fields().forEachRemaining(
                e -> result.add(e.getValue())
        );

        return result.iterator();
    }
}