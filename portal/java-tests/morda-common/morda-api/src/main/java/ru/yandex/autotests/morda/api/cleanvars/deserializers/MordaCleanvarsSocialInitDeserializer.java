package ru.yandex.autotests.morda.api.cleanvars.deserializers;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.introspect.Annotated;
import com.fasterxml.jackson.databind.introspect.JacksonAnnotationIntrospector;
import com.fasterxml.jackson.databind.type.TypeFactory;
import com.fasterxml.jackson.module.jaxb.JaxbAnnotationIntrospector;
import ru.yandex.autotests.morda.beans.cleanvars.mail.SocialInit;

import java.io.IOException;
import java.util.List;

import static com.fasterxml.jackson.databind.AnnotationIntrospector.pair;

public class MordaCleanvarsSocialInitDeserializer extends JsonDeserializer<List<SocialInit>> {

    private static final ObjectMapper om;

    static {
        om = new ObjectMapper();
        om.setAnnotationIntrospector(pair(new JaxbAnnotationIntrospector(TypeFactory.defaultInstance()) {
            @Override
            public Class<?> _doFindDeserializationType(Annotated a, JavaType baseContentType) {
                return null;
            }
        }, new JacksonAnnotationIntrospector()))
                .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
                .enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY);
    }

    @Override
    public List<SocialInit> deserialize(JsonParser jp, DeserializationContext ctxt)
            throws IOException {
        return om.readValue(jp.readValueAs(String.class),
                om.getTypeFactory().constructCollectionType(List.class, SocialInit.class));
    }
}