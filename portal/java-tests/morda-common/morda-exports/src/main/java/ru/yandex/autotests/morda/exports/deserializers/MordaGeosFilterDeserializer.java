package ru.yandex.autotests.morda.exports.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import ru.yandex.autotests.morda.exports.filters.MordaGeosFilter;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/15
 */
public class MordaGeosFilterDeserializer extends JsonDeserializer<MordaGeosFilter> {
    @Override
    public MordaGeosFilter deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        List<Integer> regions = Stream.of(p.getText().split(","))
                .map(e -> Integer.parseInt(e.trim()))
                .collect(Collectors.toList());
        return new MordaGeosFilter(regions);
    }
}
