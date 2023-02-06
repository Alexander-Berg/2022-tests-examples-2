package ru.yandex.autotests.morda.api.search.v1;

import com.bazaarvoice.jolt.Chainr;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.module.jaxb.JaxbAnnotationModule;
import ru.yandex.autotests.morda.beans.api.search.v1.SearchApiV1Response;

import java.io.IOException;

import static com.bazaarvoice.jolt.Chainr.fromSpec;
import static com.bazaarvoice.jolt.JsonUtils.classpathToList;
import static com.bazaarvoice.jolt.JsonUtils.jsonToObject;
import static com.bazaarvoice.jolt.JsonUtils.toJsonString;

public class SearchApiV1Deserializer extends JsonDeserializer<SearchApiV1Response> {

    @Override
    public SearchApiV1Response deserialize(JsonParser jp, DeserializationContext ctxt)
            throws IOException {
        String initialJson = jp.readValueAsTree().toString();

        Chainr chainr = fromSpec(classpathToList("/xsd/api/search/morda-searchapi-transform.json"));
        Object transformedObject = chainr.transform(jsonToObject(initialJson));
        String json = toJsonString(transformedObject);

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JaxbAnnotationModule());
        objectMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);

        return objectMapper.readValue(json, SearchApiV1Response.class);
    }
}