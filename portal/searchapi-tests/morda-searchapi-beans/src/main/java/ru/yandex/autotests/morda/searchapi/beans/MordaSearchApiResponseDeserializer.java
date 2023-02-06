package ru.yandex.autotests.morda.searchapi.beans;

import com.bazaarvoice.jolt.Chainr;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.introspect.JacksonAnnotationIntrospector;

import java.io.IOException;

import static com.bazaarvoice.jolt.Chainr.fromSpec;
import static com.bazaarvoice.jolt.JsonUtils.classpathToList;
import static com.bazaarvoice.jolt.JsonUtils.jsonToObject;
import static com.bazaarvoice.jolt.JsonUtils.toJsonString;

public class MordaSearchApiResponseDeserializer extends JsonDeserializer<MordaSearchApiResponse> {

    @Override
    public MordaSearchApiResponse deserialize(JsonParser jp, DeserializationContext ctxt)
            throws IOException
    {
        String initialJson = jp.readValueAsTree().toString();

        Chainr chainr = fromSpec(classpathToList("/morda-searchapi-transform.json"));
        Object transformedObject = chainr.transform(jsonToObject(initialJson));
        String json = toJsonString(transformedObject);

        ObjectMapper objectMapper = new ObjectMapper()
                .setAnnotationIntrospector(new JacksonAnnotationIntrospector());

        return objectMapper.readValue(json, MordaSearchApiResponse.class);
    }
}