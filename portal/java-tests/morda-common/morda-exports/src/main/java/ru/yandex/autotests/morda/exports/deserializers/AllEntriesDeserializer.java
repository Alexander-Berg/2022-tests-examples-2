package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;
import java.util.Iterator;

public abstract class AllEntriesDeserializer<T> extends ExportDataDeserializer<T> {
    @Override
    protected Iterator<JsonNode> getItems(JsonParser jsonParser) throws IOException {
        JsonNode root = jsonParser.readValueAs(JsonNode.class);
        return root.get("all").elements();
    }
}