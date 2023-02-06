package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static java.lang.Integer.parseInt;
import static java.util.Arrays.spliterator;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/15
 */
public class IntListDeserializer extends JsonDeserializer<List<Integer>> {
    @Override
    public List<Integer> deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        final String value = p.getText();
        final List<Integer> result = new ArrayList<>();

        if (value == null || value.isEmpty()) {
            return result;
        }

        spliterator(value.split("\\D")).forEachRemaining(
                e -> {
                    String trimmed = e.trim();
                    if (!trimmed.isEmpty()) {
                        result.add(parseInt(trimmed));
                    }
                }
        );
        return result;
    }
}
