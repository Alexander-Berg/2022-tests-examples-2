package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.datatype.joda.JodaModule;

import java.io.IOException;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.Iterator;
import java.util.List;
import java.util.Spliterator;
import java.util.stream.StreamSupport;

import static java.util.Spliterators.spliteratorUnknownSize;
import static java.util.stream.Collectors.toList;


public abstract class ExportDataDeserializer<T> extends JsonDeserializer<List<T>> {

    protected abstract Iterator<JsonNode> getItems(JsonParser jsonParser) throws IOException;

    @Override
    @SuppressWarnings("unchecked")
    public List<T> deserialize(JsonParser jsonParser, DeserializationContext deserializationContext)
            throws IOException {

        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JodaModule());
        mapper.setConfig(deserializationContext.getConfig());

        try {
            ParameterizedType parameterizedType = (ParameterizedType) this.getClass().getGenericSuperclass();
            Type t = parameterizedType.getActualTypeArguments()[0];

            final Class<T> c = (Class<T>)Class.forName(t.getTypeName());
            Iterator<JsonNode> elements = getItems(jsonParser);

            Spliterator<JsonNode> spliterator = spliteratorUnknownSize(elements, Spliterator.ORDERED);

            return StreamSupport.stream(spliterator, false)
                    .map(e -> {
                        try {
                            if (e.isObject()) {
                                ObjectNode json = e.deepCopy();
                                ObjectNode element = (ObjectNode) e;
                                element.set("json", json);
                                return mapper.readValue(element.traverse(), c);
                            } else {
                                throw new IllegalStateException("JsonNode must be object here");
                            }
                        } catch (IOException e1) {
                            throw new RuntimeException("Failed to parse export entry data", e1);
                        }
                    })
                    .collect(toList());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

}