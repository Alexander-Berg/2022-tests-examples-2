package ru.yandex.autotests.morda.api.cleanvars.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;

import java.io.IOException;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

public class MordaCleanvarsBlocksDeserializer extends JsonDeserializer<List<String>> {

    @Override
    public List<String> deserialize(JsonParser jp, DeserializationContext ctxt)
            throws IOException {

        List<List<String>> blocks = jp.readValueAs(new TypeReference<List<List<String>>>() {});

        return blocks.stream()
                .flatMap(Collection::stream)
                .collect(Collectors.toList());

    }
}