package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import static org.apache.commons.collections.IteratorUtils.toList;

public abstract class MapMapMapListDeserializer<T> extends ExportDataDeserializer<T> {

    @Override
    protected Iterator<JsonNode> getItems(JsonParser jsonParser) throws IOException {
        final JsonNode root = jsonParser.readValueAs(JsonNode.class);
        final List<JsonNode> result = new ArrayList<>();

        root.fields().forEachRemaining(
                e -> e.getValue().fields().forEachRemaining(
                        k -> k.getValue().fields().forEachRemaining(
                                s -> result.addAll(toList(s.getValue().elements()))
                        )
                )
        );

        return result.iterator();
    }
}